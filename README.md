# Sci_literature_download_review
I wrote the code to automate the workflow for scientists to collect research papers. The code walks through the process of "searching for papers by keywords," "collecting paper information," "downloading PDF versions," and "analyzing the abstracts." The code consists of seven classes, in which the Main() class walks through the entire work cycle, and the other six classes each handle one type of task. The Springer Open Access API was used here, which provides metadata and full-text content for more than 649,000 open access articles. And since it's an open-access scholar search engine, users should be able to download full-text versions without a journal subscription.
Below is the flow chart of the code:

![image](https://user-images.githubusercontent.com/74574958/157773182-3d459493-c8f4-48a0-99a0-dce50b8b2ab2.png)

Future work:
    In this code, I applied the Gensim library (3.8.3) to conduct some basic text processing on the abstracts. I plan to use advanced NLP techniques in the future to process the abstracts or even the full article content.
