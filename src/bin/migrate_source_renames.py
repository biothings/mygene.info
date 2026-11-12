#!/usr/bin/env python
"""
One-off migration of the hub's data for the source renames:

    ncbi_gene      -> ncbi_gene_summary   (the gene-summary source; frees the name "ncbi_gene")
    entrez         -> ncbi_gene           (uploaders entrez_* -> ncbi_gene_*)
    entrez_unigene -> unigene
    mygene_unii    -> unii

Stop the hub and move the data folders first. Then, from src/ with the hub's venv:

    python bin/migrate_source_renames.py               # dry run: report what --apply would do
    python bin/migrate_source_renames.py --apply
    python bin/migrate_source_renames.py --rollback    # undo --apply (before --cleanup)
    python bin/migrate_source_renames.py --cleanup     # after the first release note with the new names

--apply
  * renames each uploader's collection in the source database
  * copies the GridFS file read by the build's retired-ID mapper to its new name
  * src_dump: adds each source's document under its new _id, with its jobs and data folders
    renamed. The old entrez, entrez_unigene and mygene_unii documents stay, marked with
    "renamed_to" and without pending flags: the release note looks up the previous build's
    sources there. The ncbi_gene document moves to ncbi_gene_summary, since entrez takes its _id.
  * src_master: adds each uploader's document under its new name
  * src_build_config: renames the sources in every build configuration
  * hub_config: renames class settings changed in the hub ("<class>.<ATTR>", e.g. a dumper's
    SCHEDULE) to the renamed classes. NcbiGeneDumper was the summary dumper's class and is now
    the entrez dumper's, so its settings move to NcbiGeneSummaryDumper first.
  Every step skips what's already done, so --apply can be run again after a failure.

--rollback puts everything back as it was before --apply, as long as the hub hasn't dumped or
uploaded these sources under their new names since. Move the data folders back first.

--cleanup deletes what --apply kept: the old src_dump and src_master documents and the old
GridFS file.
"""

import argparse
import copy
import logging
import os
import re
import sys

for _name in ("pymongo", "git", "elasticsearch", "urllib3"):
    logging.getLogger(_name).setLevel(logging.WARNING)

SRC_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_FOLDER not in sys.path:
    sys.path.insert(0, SRC_FOLDER)

import biothings.hub  # noqa: E402,F401  (loads config.py the way the hub does)
import gridfs  # noqa: E402
from biothings import config  # noqa: E402
from biothings.utils.mongo import (  # noqa: E402
    get_hub_config,
    get_src_build_config,
    get_src_db,
    get_src_dump,
    get_src_master,
)

# (old src_dump _id, new src_dump _id, {old uploader name: new uploader name}), in migration order:
# ncbi_gene has to move before entrez takes its _id.
SOURCES = [
    ("ncbi_gene", "ncbi_gene_summary", {"ncbi_gene": "ncbi_gene_summary"}),
    (
        "entrez",
        "ncbi_gene",
        {
            "entrez_gene": "ncbi_gene_info",
            "entrez_accession": "ncbi_gene_accession",
            "entrez_go": "ncbi_gene_go",
            "entrez_genomic_pos": "ncbi_gene_genomic_pos",
            "entrez_retired": "ncbi_gene_retired",
            "entrez_refseq": "ncbi_gene_refseq",
        },
    ),
    ("entrez_unigene", "unigene", {"entrez_unigene": "unigene"}),
    ("mygene_unii", "unii", {"mygene_unii": "unii"}),
]
# old -> new uploader names, which are also the collection names
UPLOADERS = {old: new for _, _, uploaders in SOURCES for old, new in uploaders.items()}
GRIDFS_FILES = {"entrez_gene__geneid_d.pyobj": "ncbi_gene_info__geneid_d.pyobj"}
# the source whose old src_dump document is replaced rather than kept
REPLACED = "ncbi_gene"
# (old class name, new class name), in migration order: NcbiGeneDumper is freed before it's reused
CLASSES = [
    ("NcbiGeneDumper", "NcbiGeneSummaryDumper"),
    ("EntrezGeneDumper", "NcbiGeneDumper"),
    ("EntrezGeneUploader", "NcbiGeneInfoUploader"),
    ("EntrezAccessionUploader", "NcbiGeneAccessionUploader"),
    ("EntrezGOUploader", "NcbiGeneGOUploader"),
    ("EntrezGenomicPosUploader", "NcbiGeneGenomicPosUploader"),
    ("EntrezRetiredUploader", "NcbiGeneRetiredUploader"),
    ("EntrezRefseqUploader", "NcbiGeneRefseqUploader"),
    ("EntrezUnigeneDumper", "UnigeneDumper"),
    ("EntrezUnigeneUploader", "UnigeneUploader"),
    ("MyGeneUNIIDumper", "UniiDumper"),
]


def class_settings(cls):
    """hub_config query for the settings of one class: _id "<class>.<ATTR>"."""
    return {"_id": {"$regex": "^%s\\.[^.]+$" % re.escape(cls)}}


class Problem(Exception):
    pass


def moved(path, old, new):
    """'/data/entrez/20261031' -> '/data/ncbi_gene/20261031'; other paths are returned as they are."""
    if not isinstance(path, str) or not path:
        return path
    parent, release = os.path.split(path.rstrip("/"))
    root, name = os.path.split(parent)
    if name != old:
        return path
    return os.path.join(root, new, release)


def renamed_doc(doc, new_id, old_src, new_src, uploaders):
    """
    Copy of a src_dump document for its new name: jobs (upload, inspect, ...) renamed, jobs of
    other uploaders left out, data folders moved. Returns (copy, names of the jobs left out).
    """
    doc = copy.deepcopy(doc)
    doc["_id"] = new_id
    dropped = set()
    for section in doc.values():
        if isinstance(section, dict) and isinstance(section.get("jobs"), dict):
            jobs = {}
            for name, job in section["jobs"].items():
                if name not in uploaders:
                    dropped.add(name)
                    continue
                if isinstance(job, dict):
                    if job.get("step") == name:
                        job["step"] = uploaders[name]
                    if "data_folder" in job:
                        job["data_folder"] = moved(job["data_folder"], old_src, new_src)
                jobs[uploaders[name]] = job
            section["jobs"] = jobs
    for section in (doc, doc.get("download")):
        if isinstance(section, dict) and "data_folder" in section:
            section["data_folder"] = moved(section["data_folder"], old_src, new_src)
    return doc, sorted(dropped)


def data_folders(doc):
    folders = {doc.get("data_folder"), (doc.get("download") or {}).get("data_folder")}
    for section in doc.values():
        if isinstance(section, dict) and isinstance(section.get("jobs"), dict):
            folders.update(job.get("data_folder") for job in section["jobs"].values() if isinstance(job, dict))
    return {f for f in folders if isinstance(f, str) and f}


def running_jobs(doc):
    """Statuses like 'downloading' or 'uploading' left in a src_dump document."""
    found = []
    if str((doc.get("download") or {}).get("status", "")).endswith("ing"):
        found.append("download: %s" % doc["download"]["status"])
    for key, section in doc.items():
        if isinstance(section, dict) and isinstance(section.get("jobs"), dict):
            for name, job in section["jobs"].items():
                if isinstance(job, dict) and str(job.get("status", "")).endswith("ing"):
                    found.append("%s.%s: %s" % (key, name, job["status"]))
    return found


def mask(uri):
    return re.sub(r"//[^@/]+@", "//***@", str(uri))


class Migration:
    def __init__(self, mode, ignore_status=False):
        self.write = mode != "dry run"
        self.ignore_status = ignore_status
        self.src_db = get_src_db()
        self.dump = get_src_dump()
        self.master = get_src_master()
        self.build_config = get_src_build_config()
        self.hub_config = get_hub_config()
        self.fs = gridfs.GridFS(self.src_db)
        self.problems = []
        self.warnings = []

    def say(self, msg):
        print(("  " if self.write else "  would ") + msg)

    def find(self, _id):
        return self.dump.find_one({"_id": _id})

    # ------------------------------------------------------------------ checks

    def check_status(self, doc):
        if doc and not self.ignore_status:
            for job in running_jobs(doc):
                self.problems.append(
                    "src_dump %s has a running job (%s). Stop the hub and let its jobs finish; if no hub is "
                    "running, the status is left over from an interrupted job: rerun with --ignore-status."
                    % (doc["_id"], job)
                )

    def check_folders(self, renamed, old_src, new_src):
        """The data folders a renamed src_dump document points to have to exist: the folders were moved."""
        for new_path in sorted(data_folders(renamed)):
            old_path = moved(new_path, new_src, old_src)
            if new_path == old_path or os.path.exists(new_path):
                continue
            old_root = os.path.dirname(old_path.rstrip("/"))
            new_root = os.path.join(os.path.dirname(old_root), new_src)
            if os.path.exists(old_path):
                self.problems.append("%s hasn't been moved: mv %s %s" % (old_path, old_root, new_root))
            elif os.path.exists(os.path.join(new_root, old_src)):
                self.problems.append("%s was moved inside %s instead of renamed to it" % (old_root, new_root))
            else:
                self.warnings.append(
                    "neither %s nor %s exists (fine if that release's files were deleted)" % (old_path, new_path)
                )

    # ------------------------------------------------------------------ apply

    def check_apply(self):
        cols = set(self.src_db.list_collection_names())
        for old, new in UPLOADERS.items():
            if old in cols and new in cols:
                self.problems.append("collections %s and %s both exist" % (old, new))
        for old, new, uploaders in SOURCES:
            old_doc, new_doc = self.find(old), self.find(new)
            if old == REPLACED and old_doc and old_doc.get("renamed_from"):
                old_doc = None  # already holds the migrated entrez document
            for doc in (old_doc, new_doc):
                self.check_status(doc)
            if not old_doc or (new_doc and new_doc.get("renamed_from") == old):
                continue  # nothing to migrate, or done already
            # the new _id has to be free, except ncbi_gene: the first step moves that document away
            if new_doc and not (new == REPLACED and not new_doc.get("renamed_from")):
                self.problems.append(
                    "src_dump already has a %s document that this script didn't make; "
                    "was the hub started with the new code before the migration?" % new
                )
            self.check_folders(renamed_doc(old_doc, new, old, new, uploaders)[0], old, new)
        moving = self.class_settings_to_rename()
        for doc, new_id in moving:
            if self.hub_config.find_one({"_id": new_id}) and new_id not in {d["_id"] for d, _ in moving}:
                self.problems.append("hub_config already has %s; can't rename %s to it" % (new_id, doc["_id"]))

    def class_settings_to_rename(self):
        """[(hub_config doc, new _id)] for class settings still under an old class name."""
        found = []
        for old_cls, new_cls in CLASSES:
            for doc in self.hub_config.find(class_settings(old_cls)):
                if not doc.get("renamed_from"):
                    found.append((doc, new_cls + doc["_id"][len(old_cls) :]))
        return found

    def apply_hub_config(self):
        print("hub_config (class settings changed in the hub):")
        renamed = False
        for old_cls, new_cls in CLASSES:  # one class at a time, so NcbiGeneDumper is free before it's reused
            for doc in list(self.hub_config.find(class_settings(old_cls))):
                if doc.get("renamed_from"):
                    continue
                new_id = new_cls + doc["_id"][len(old_cls) :]
                self.say("rename %s -> %s (value %s)" % (doc["_id"], new_id, doc.get("json")))
                renamed = True
                if self.write:
                    self.hub_config.insert_one(dict(doc, _id=new_id, renamed_from=doc["_id"]))
                    self.hub_config.delete_one({"_id": doc["_id"]})
        if not renamed:
            print("  nothing to rename")

    def apply_collections(self):
        print("Collections in %s:" % self.src_db.name)
        cols = set(self.src_db.list_collection_names())
        for old, new in UPLOADERS.items():
            if new in cols and old not in cols:
                print("  %s: already renamed" % new)
            elif old in cols:
                self.say("rename %s -> %s (%s docs)" % (old, new, f"{self.src_db[old].estimated_document_count():,}"))
                if self.write:
                    self.src_db[old].rename(new)
            else:
                self.warnings.append("no %s collection to rename" % old)
        others = sorted(c for c in cols if re.match(r"(entrez|mygene_unii)", c) and c not in UPLOADERS)
        if others:
            print("  not touched (not uploader collections): %s" % ", ".join(others))

    def apply_gridfs(self):
        print("GridFS files in %s:" % self.src_db.name)
        for old, new in GRIDFS_FILES.items():
            if self.fs.exists(new):
                print("  %s: already there" % new)
            elif self.fs.exists(old):
                self.say("copy %s -> %s" % (old, new))
                if self.write:
                    self.fs.put(self.fs.get(old), _id=new, filename=new)
            else:
                self.warnings.append("no GridFS file %s: upload ncbi_gene_info before the next build" % old)

    def apply_src_dump(self):
        print("src_dump:")
        for old, new, uploaders in SOURCES:
            new_doc = self.find(new)
            if new_doc and new_doc.get("renamed_from") == old:
                print("  %s: already migrated" % new)
                continue
            old_doc = self.find(old)
            if old == REPLACED and old_doc and old_doc.get("renamed_from"):
                old_doc = None
            if not old_doc:
                self.warnings.append("no src_dump document for %s" % old)
                continue
            doc, dropped = renamed_doc(old_doc, new, old, new, uploaders)
            doc["renamed_from"] = old
            jobs = ", ".join(sorted((doc.get("upload") or {}).get("jobs", {}))) or "none"
            folder = (doc.get("download") or {}).get("data_folder")
            detail = "upload jobs: %s; data folder: %s" % (jobs, folder)
            if old == REPLACED:
                self.say("move %s -> %s (%s)" % (old, new, detail))
            else:
                self.say("copy %s -> %s (%s), keep %s for the release note" % (old, new, detail, old))
            if dropped:
                print("    leaving out jobs of other uploaders: %s" % ", ".join(dropped))
            if self.write:
                self.dump.insert_one(doc)
                if old == REPLACED:
                    self.dump.delete_one({"_id": old})
                else:
                    self.dump.update_one({"_id": old}, {"$set": {"renamed_to": new}, "$unset": {"pending": ""}})

    def apply_src_master(self):
        print("src_master:")
        for old, new in UPLOADERS.items():
            if self.master.find_one({"_id": new}):
                print("  %s: already there" % new)
                continue
            doc = self.master.find_one({"_id": old})
            if not doc:
                self.warnings.append("no src_master document for %s" % old)
                continue
            doc["_id"] = new
            if doc.get("name") == old:
                doc["name"] = new
            self.say("copy %s -> %s" % (old, new))
            if self.write:
                self.master.insert_one(doc)

    def rename_build_configs(self, names):
        print("src_build_config:")
        for conf in self.build_config.find():
            update = {}
            for key in ("sources", "root"):
                values = conf.get(key)
                if not isinstance(values, list):
                    continue
                renamed = []
                for value in values:
                    prefix, name = ("!", value[1:]) if str(value).startswith("!") else ("", value)
                    renamed.append(prefix + names.get(name, name))
                    if name not in names and re.search(r"[.*+?\[\]()|^$\\]", str(name)):
                        try:
                            matches = [n for n in names if re.fullmatch(str(name), n)]
                        except re.error:
                            matches = []
                        if matches:
                            self.warnings.append(
                                "build config %s: %r in %s matches %s; edit it by hand"
                                % (conf["_id"], value, key, ", ".join(matches))
                            )
                if renamed != values:
                    update[key] = renamed
                    changes = ["%s -> %s" % (a, b) for a, b in zip(values, renamed) if a != b]
                    self.say("rename in %s.%s: %s" % (conf["_id"], key, ", ".join(changes)))
            if not update:
                print("  %s: nothing to rename" % conf["_id"])
            elif self.write:
                self.build_config.update_one({"_id": conf["_id"]}, {"$set": update})

    def apply(self):
        self.check_apply()
        self.stop_on_problems()
        self.apply_collections()
        self.apply_gridfs()
        self.apply_src_dump()
        self.apply_src_master()
        self.rename_build_configs(UPLOADERS)
        self.apply_hub_config()

    # ------------------------------------------------------------------ rollback

    def check_rollback(self):
        cols = set(self.src_db.list_collection_names())
        for old, new in UPLOADERS.items():
            if old in cols and new in cols:
                self.problems.append("collections %s and %s both exist" % (old, new))
        for old, new, uploaders in reversed(SOURCES):  # ncbi_gene's folder has to go back to entrez first
            new_doc = self.find(new)
            if not (new_doc and new_doc.get("renamed_from") == old):
                continue
            self.check_status(new_doc)
            restored, _ = renamed_doc(new_doc, old, new, old, {v: k for k, v in uploaders.items()})
            self.check_folders(restored, new, old)
            if old == REPLACED:
                continue
            old_doc = self.find(old)
            if not old_doc:
                self.problems.append("src_dump %s is gone (--cleanup ran?): restore the hub DB from a backup" % old)
                continue
            # the kept document is what comes back, so nothing may have happened under the new name since
            for name, job in (restored.get("upload") or {}).get("jobs", {}).items():
                old_job = (old_doc.get("upload") or {}).get("jobs", {}).get(name) or {}
                if job.get("started_at") != old_job.get("started_at"):
                    self.problems.append(
                        "%s has been uploaded since --apply; rolling back would lose that: "
                        "restore the hub DB from a backup instead" % uploaders[name]
                    )
            if (new_doc.get("download") or {}).get("release") != (old_doc.get("download") or {}).get("release"):
                self.problems.append(
                    "%s has been dumped since --apply; rolling back would lose that: "
                    "restore the hub DB from a backup instead" % new
                )

    def rollback(self):
        self.check_rollback()
        self.stop_on_problems()
        print("hub_config (class settings changed in the hub):")
        for old_cls, new_cls in reversed(CLASSES):  # NcbiGeneDumper goes back to EntrezGeneDumper first
            for doc in list(self.hub_config.find(class_settings(new_cls))):
                if not str(doc.get("renamed_from", "")).startswith(old_cls + "."):
                    continue
                self.say("rename %s -> %s" % (doc["_id"], doc["renamed_from"]))
                if self.write:
                    restored = {k: v for k, v in doc.items() if k != "renamed_from"}
                    restored["_id"] = doc["renamed_from"]
                    self.hub_config.insert_one(restored)
                    self.hub_config.delete_one({"_id": doc["_id"]})
        self.rename_build_configs({v: k for k, v in UPLOADERS.items()})
        print("src_master:")
        for old, new in UPLOADERS.items():
            if self.master.find_one({"_id": new}) and self.master.find_one({"_id": old}):
                self.say("delete %s (%s is still there)" % (new, old))
                if self.write:
                    self.master.delete_one({"_id": new})
        print("src_dump:")
        for old, new, uploaders in reversed(SOURCES):
            new_doc = self.find(new)
            if not (new_doc and new_doc.get("renamed_from") == old):
                print("  %s: nothing to roll back" % new)
                continue
            if old == REPLACED:
                restored, _ = renamed_doc(new_doc, old, new, old, {v: k for k, v in uploaders.items()})
                restored.pop("renamed_from")
                self.say("move %s -> %s" % (new, old))
                if self.write:
                    self.dump.insert_one(restored)
                    self.dump.delete_one({"_id": new})
            else:
                self.say("delete %s, restore %s" % (new, old))
                if self.write:
                    update = {"$unset": {"renamed_to": ""}}
                    if new_doc.get("pending"):
                        update["$set"] = {"pending": new_doc["pending"]}
                    self.dump.update_one({"_id": old}, update)
                    self.dump.delete_one({"_id": new})
        print("GridFS files in %s:" % self.src_db.name)
        for old, new in GRIDFS_FILES.items():
            if self.fs.exists(new):
                if not self.fs.exists(old):
                    self.say("copy %s -> %s" % (new, old))
                    if self.write:
                        self.fs.put(self.fs.get(new), _id=old, filename=old)
                self.say("delete %s" % new)
                if self.write:
                    self.fs.delete(new)
        print("Collections in %s:" % self.src_db.name)
        cols = set(self.src_db.list_collection_names())
        for old, new in UPLOADERS.items():
            if new in cols and old not in cols:
                self.say("rename %s -> %s" % (new, old))
                if self.write:
                    self.src_db[new].rename(old)

    # ------------------------------------------------------------------ cleanup

    def cleanup(self):
        for old, new, _ in SOURCES:
            new_doc = self.find(new)
            if not (new_doc and new_doc.get("renamed_from") == old):
                self.problems.append("src_dump %s isn't migrated yet: run --apply first" % new)
        self.stop_on_problems()
        print("src_dump:")
        for old, new, _ in SOURCES:
            if old == REPLACED:
                continue
            old_doc = self.find(old)
            if old_doc and old_doc.get("renamed_to") == new:
                self.say("delete %s" % old)
                if self.write:
                    self.dump.delete_one({"_id": old})
        print("src_master:")
        for old, new in UPLOADERS.items():
            if self.master.find_one({"_id": old}) and self.master.find_one({"_id": new}):
                self.say("delete %s" % old)
                if self.write:
                    self.master.delete_one({"_id": old})
        print("GridFS files in %s:" % self.src_db.name)
        for old, new in GRIDFS_FILES.items():
            if self.fs.exists(old) and self.fs.exists(new):
                self.say("delete %s" % old)
                if self.write:
                    self.fs.delete(old)

    # ------------------------------------------------------------------

    def stop_on_problems(self):
        if self.problems:
            raise Problem("\n".join("  - " + p for p in dict.fromkeys(self.problems)))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--apply", action="store_true", help="migrate (default: dry run)")
    action.add_argument("--rollback", action="store_true", help="undo --apply")
    action.add_argument("--cleanup", action="store_true", help="delete the old documents --apply kept")
    parser.add_argument("--dry-run", action="store_true", help="only report what --apply/--rollback/--cleanup would do")
    parser.add_argument("--yes", action="store_true", help="don't ask for confirmation")
    parser.add_argument("--ignore-status", action="store_true", help="ignore running-job statuses in src_dump")
    args = parser.parse_args()

    step = "rollback" if args.rollback else "cleanup" if args.cleanup else "apply"
    dry = args.dry_run or not (args.apply or args.rollback or args.cleanup)
    print("config:        %s" % sys.modules["config"].__file__)
    print("hub DB:        %s / %s" % (mask(config.HUB_DB_BACKEND.get("uri")), config.DATA_HUB_DB_DATABASE))
    print(
        "source DB:     %s:%s / %s"
        % (config.DATA_SRC_SERVER, getattr(config, "DATA_SRC_PORT", 27017), config.DATA_SRC_DATABASE)
    )
    print("step:          %s%s\n" % (step, " (dry run, nothing is changed)" if dry else ""))
    if not dry and not args.yes:
        if input("Stop the hub before going on. Type 'yes' to %s: " % step).strip() != "yes":
            sys.exit("Nothing changed.")

    migration = Migration("dry run" if dry else step, ignore_status=args.ignore_status)
    try:
        getattr(migration, step)()
    except Problem as problems:
        sys.exit("Nothing changed. Fix these first:\n%s" % problems)
    for warning in dict.fromkeys(migration.warnings):
        print("warning: %s" % warning)
    print("\n%s." % ("Dry run done, nothing changed" if dry else "Done"))


if __name__ == "__main__":
    main()
