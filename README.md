# MicRou
## Introduction
The documents that constitute the dataset were gathered for a RAG project in memory of [Michel Rouger](https://www.pitti.io/articles/michel-rouger) : the documents were part of his personal archives and include his own work as well as work produced by other authors during projects he ran.

## Datasets
This repository includes 2 datasets in French:  

1. microu  

This dataset includes approximately 850 documents in French (books, articles, minutes of debates) produced between 1998 and 2020. It covers justice and law, finance and economics, management, healthcare, education, sports, history and geopolitics... Overall it represents between 1.5m and 2m tokens depending on the tokenizer you use.  

In many cases, the documents stem from a larger source that was broken down as parts could be considered independently (e.g. different chapters of a book or different articles of a newsletter). It is nonetheless possible to recombine the entire source : within a "dossier", you can group by date and, within each group, order by index. Documents that do not come from a larger source have an index of 0 by default.

2. microu-chunked  

As part of the RAG projet, we used an embeddings model, [Solon](https://huggingface.co/OrdalieTech/Solon-embeddings-large-0.1), with a context window of 512 tokens so we had to split the MicRou dataset into chunks. This is the resulting dataset.



https://github.com/pappitti/MicRou/assets/90358606/d262101b-387f-41b5-8393-c92f5170b306



The chunking strategy leveraged the existing sections of the documents as much as possible using a recursive function:
- starting from the top, split the document into sections based on markdown headings level (starting from level 1). 
- tokenize the resulting sections and check if they fit into the maximum number of tokens
- if a section fits, save the chunk (it guarantees that a section is not split). If not, apply the same process to the section but this time splitting the text based on headings at a level below. The recursive function drills down the sections each time the text does not fit.
- if there is no headings in the text, the function looks for lists (ordered or unordered) and breaks down the text accordingly.
- if there is no list, the text is broken down into paragraphs and if paragraphs are still too large, they are further broken down into sentences. 
- Finally, starting from the most granular level of each subsection (bottom-up), chunks are re-aggregated with an algorithm that looks for the minimal number of groups that can be formed with the chunks whilst respecting the constraints of the maximum tokens by chunks. Nothing too fancy : this is brute-force optimization.  

The python script used for chunking is included in the chunking folder of this repository.  

## License (CC-BY-NC-SA-4.0)  
The dataset is currently under restrictive license. We plan to convert it to an open license once we have finalized the review of the right holders. Some documents may be excluded following the review, but we also plan to add others over time.

## Next Steps 
It is currently envisaged to build a web app that lets user query and navigate the dataset, and potentially generate summaries based on retrieved chunks.  
  
In the meantime, Tensorflow's [Embeddings Projector](https://projector.tensorflow.org/) is a good tool to explore the dataset. Here is how to use it:
1. download the 2 tsv files for the [microu-chunked embeddings](https://pitti-backend-assets.ams3.cdn.digitaloceanspaces.com/michel-rouger/embeddings.tsv) and the [metadata](https://pitti-backend-assets.ams3.cdn.digitaloceanspaces.com/michel-rouger/metadata.tsv).
2. once on [Embeddings Projector](https://projector.tensorflow.org/), click on the load button (on the left-hand side)
3. follow the instructions to uplead the two tsv files  

By default, dimension reduction is done with PCA but you may find UMAP (bottom left) more user-friendly 
