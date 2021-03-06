from urllib import urlencode as uencode, urlopen as uopen
from BeautifulSoup import BeautifulSoup
import numpy as np
import networkx as nx
from matplotlib import pyplot as plt
from textwrap import wrap

class path:
    def __init__(self,souptag):
        self.text = souptag.text.encode('utf8')
        self.target_num=int(souptag.attrMap['data-target-node'])
    def __str__(self):
        return 'Node {0}: {1}'.format(self.target_num,self.text)
    def __repr__(self):
        return self.__str__()

class Adventure:
    def __init__(self,url):
        '''Takes url of ClickVenture, creates Adventure object. Call `graph` method to make/show the graph.'''
        self.url = url
        page=uopen(url)
        self.soup=BeautifulSoup(page)
        self.G = None #will be replaced by graph later
        
        #get page title
        title_tag=self.soup.find('div',attrs={'class':'share-buttons share-widget'})
        self.title=title_tag.attrMap['data-share-title']
        
    def graph(self,figsize=30,showPlot=False,save=False,save_folder=r'./ClickVenture Results/',wrap_width = 25,**kwargs):
        '''Creates a networkx graph object from the HTML data, and shows/saves the graph if desired. 
        
        
        INPUTS:
        ------
        figsize: size (length and width) of the produced matplotlib figure
        save: should this be saved?
        save_folder: where it gets saved
        wrap_width: when the plot title gets wrapped, how many columns should be the maximum?
        **kwargs - the rest of the keyword arguments get shoved into networkx.draw
        
        -------
        Stores the networkx object in self.G. Other attributes:
        self.n_nodes - 
        self.degrees - 
        '''
        if self.G is None: #if no graph has been generated yet, make one. This prevents having to do all the calculations each time if they've already been done.
            arrows=[]
            
            #starting at mother node
            mother_node = self.soup.find('div',attrs={'class':'clickventure-node clickventure-start '})
            self.mother_id = int(mother_node.attrMap['data-node-id'])
            mother_paths = [path(item) for item in mother_node.findAll('div',attrs={'class':'clickventure-node-link '})] #finding all the paths that start from this node
            for initial_path in mother_paths:
                arrows.append((self.mother_id,initial_path.target_num))
            
            #creating list of edges
            for found_node in self.soup.findAll('div',attrs={'class':'clickventure-node  '}):#searching for node <div> tags, iterating through each of them
                node_id = int(found_node.attrMap['data-node-id']) #getting the node id
                paths = [path(item) for item in found_node.findAll('div',attrs={'class':'clickventure-node-link '})] #finding all the paths that start from this node
                #print node_id
                for found_path in paths: #adding an edge for each path
                    #print '\t {0}'.format(found_path.target_num)
                    arrows.append((node_id,found_path.target_num))
            
            self.arrows=arrows
            #creating networkx graph using the connections found above
            self.G=nx.DiGraph()
            self.G.add_edges_from(arrows)
        
        #creating node number variable
        self.n_nodes = len(self.G.nodes())
        
        #figuring out node sizes
        self.degrees=np.array(self.G.degree().values()) #number of edges for each node
        degree_max = float(max(self.degrees))
        adjusted_node_size = 300*np.exp(3.5*self.degrees/degree_max) #adjusting node sizes so ones with more connections look a lot bigger
        
        #graphing stuff
        if showPlot:
            #creating figure and drawing graph
            fig=plt.figure(figsize=(figsize,figsize))
            nx.draw_spring(self.G,
                   node_size=adjusted_node_size,
                   **kwargs)

            #wrapping and showing title
            wrapped_title = '\n'.join(wrap(self.title,wrap_width))
            plt.title(wrapped_title,size=figsize*2,y=0.9)

            #saving
            if save:
                plt.savefig(save_folder+self.title+'.png')

            plt.show()
        
        
    def __str__(self):
        return "~~CLICKHOLE CLICKVENTURE: {0}~~".format(self.title.encode('utf8'))
    def __repr__(self):
        return self.__str__()
        
    class node:
        def __init__(self,num,soup):
            res = soup.find('div',attrs={'data-node-id':num})
            self.paths = [path(item) for item in res.findAll('div',attrs={'class':'clickventure-node-link '})]
            self.text = res.text
        
############################

##getting all adventure URLs
articles=[] #list to put article URLs in
for pageno in [1,2,3]:
    list_URL = r'http://www.clickhole.com/features/clickventure/?page={0}'.format(pageno)
    list_page=uopen(list_URL)
    list_soup = BeautifulSoup(list_page)

    for article_soup in list_soup.findAll('article'):
        link_tag = article_soup.findAll('a')[0] #finding the link tag within the HTML
        article_url = r'http://clickhole.com' + link_tag.attrs[1][1] #getting the href component of the link attribute
        articles.append(article_url) #adding URL to master list

print 'Found ' + str(len(articles)) + ' articles.'


#making Adventure objects and generating/saving graphs. Make sure ../ClickVenture Results folder exists
adventures=[] #list that will hold Adventure objects
for article_url in articles:
    try:
        ClickVenture = Adventure(article_url)
        adventures.append(ClickVenture)
        ClickVenture.graph(save=True,alpha=0.7,node_color='seagreen',figsize=10,wrap_width=60)
    except:
        print 'Failed to process ' + article_url
   