<dataConfig>
  <dataSource type="FileDataSource" name="fds" />
  <document>
    <entity name="dblp"
	    processor="XPathEntityProcessor"
	    xsl='conf/xslt/gen.xsl'
	    dataSource="fds"
	    url="${solr.install.dir}/dblp.xml"
	    onError="abort"
	    stream="true"
	    useSolrAddSchema="true">
    </entity>
    
  </document>
</dataConfig>
