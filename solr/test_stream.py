import asyncio

from solr.instances import get_localhost_session, get_async_localhost_session
import solr.api.stream.sources as sources
import solr.api.stream.decorators as decorators
import jsonstreamer


def _catch_all(event_name, *args):
    print('\t{} : {}'.format(event_name, args))


async def streaming(search):
    s = get_async_localhost_session()
    streamer = jsonstreamer.JSONStreamer()
    # objstream = jsonstreamer.ObjectStreamer()
    # objstream.auto_listen()
    streamer.add_catch_all_listener(_catch_all)
    async with s.collection('s2').stream.expr(search) as stream:
        while True:
            chunk = await stream.content.read(20)
            if not chunk:
                break
            streamer.consume(chunk.decode('utf-8'))
    streamer.close()
    await s.close()

async def main():

    paper_w_citations = sources.Search('s2', 'authors.name:"Timo Ropinski"', 'id,title,doi', 'id asc', qt='/export')
    id2citations = decorators.CartesianProduct(paper_w_citations, "outCitations")
    cited_nodes = sources.Nodes('s2', 'outCitations->id', 'title', paper_w_citations, scatter='branches, leaves', trackTraversal=True)
    node_with_citation = sources.Nodes('s2', 'outCitations->id', 'id', id2citations, scatter='branches, leaves', trackTraversal=True)
    papers = sources.Search('s2', 'authors.name:Timo\ Ropinski', 'id,title,outCitations', 'id asc', rows=1)
    papers = decorators.CartesianProduct(papers, "outCitations")
    papers = sources.Nodes('s2','out->id', 'title', papers, scatter='branches, leaves')
    await streaming(paper_w_citations)
    # r = s.collection('s2').graph.expr(traverse_out)
    # print(r.text)

    # search for an authors name via faceting:
    # http://localhost:8983/solr/s2/select?f.authors.name.facet.contains=Ropinski&facet.field=authors.name&facet=on&q=authors.name:*Ropinski*&rows=0
    print(f'sent: {paper_w_citations}')

if __name__ == '__main__':
    asyncio.run(main())