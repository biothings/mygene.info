# BioThings API Specifications 
BioThings APIs are APIs designed for biological entities. Here are the guidelines to follow when building a new BioThings API:

### 1. Endpoints
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BioThings API supports the following endpoints:
  - Query Service --- make query about a specific field, and return a list of matching entities
```
      http://myvariant.info/v1/query?q=_exists_:exac
```
  - Entity Retrieval Service --- retrieve annotation based on an ID, e.g. HGVS ID
```
      http://myvariant.info/v1/variant/chr6:g.26093141G>A
```
  - Metadata Retrieval Service --- retrieve metadata about the data available
```
      http://myvariant.info/v1/metadata
```
### 2. Versioning
  - Include the version number (as "v1", "v2", "v3", and so on) to the endpoint URLs (e.g. http://myvariant.info/v1/variant endpoint)
  - Increase version number when breaking changes are introduced to the API
  
### 3. Supported HTTP Methods
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BioThings API endpoints support both ‘GET’ and ‘POST’ HTTP methods:
  - GET: perform a single entity-retrieval or a single query
  - POST: perform a batch of entity-retrieval or queries
  
### 4. Supported data formats
  - JSON
  - Msgpack  (a binary JSON format, optional)
  
### 5. CORS support
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Biothings API endpoints support [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS) with unrestricted hostnames, so that users can make cross-origin API requests directly from their web application.

### 6. JSONP support
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Biothings API endpoints support [JSONP](https://remysharp.com/2007/10/08/what-is-jsonp) [(also see here)](https://en.wikipedia.org/wiki/JSONP#JSONP) with a query parameter “callback”, so that users can make JSONP API requests directly from their web applications.

### 7. HTTPS support
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BioThings API endpoints support both HTTP and HTPPS protocol, so that users can make encrypted API request if needed.

### 8. HTTP compression support
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BioThings API endpoints support gzip HTTP compression protocol to reduce the data transfer size.

### 9. HTTP caching support
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BioThings API endpoints support HTTP caching headers with both “Cache-Control” and “etag” headers (max-age is set to 7 days).

### 10. Common Parameters

 * Common parameter(s) supported by both query and entity retrieval services

    * fields
       * Use comma-separated fields to limit the fields returned from the variant object.
       * Use dot notation to return a field in a nested structure, e.g.“cadd.gene”.
       * Default: “fields=all”. If “fields=all”, all available fields will be returned.
       
    * callback
       * Optional
       * pass a “callback” parameter to make a JSONP call.
```
    https://myvariant.info/v1/variant/chr6:26093141G>A?fields=clinvar.rcv.conditions, dbsnp
```


 * Common parameters supported only by query service

    * size
       * The maximum number of matching object hits to return
       * Optional, default is 10

    * from
       * The number of matching hits to skip
       * Optional, default is 0
  
```
    https://mygene.info/v3/query?q=cdk2&size=50&from=20
```
