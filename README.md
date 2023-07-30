# readtimelines.com

# How it works

**Data Source**

- After faffing around with various news APIs we decided to build [our own](https://github.com/trollers-dev/timelines-data/)

- Our news data is kept in a Meilisearch instance, which is a lightweight fulltext search engine originally designed for fast client-facing search. However, our scale and speed requirements fit Meilisearch perfectly, and it's lightweight nature helps us to save on cost. We host our Meilisearch instance on DigitalOcean.

- Here's what the news articles look like (embeddings truncated for ease of viewing):
  
  ```json
  [
      {
          "title": "China hopes France can help take heat out of relations with EU",
          "description": "China hopes France can \"stabilise the tone\" of EU-China relations, vice-premier He Lifeng told his French counterpart in Beijing on ...",
          "content": "BEIJING, July 29  - China hopes France can \"stabilise the tone\" of EU-China relations, vice-premier He Lifeng told his French counterpart...","
          "thumbnailUrl": "https://www.reuters.com/resizer/HJFF_pY0mp8L296eXv2plFEmbps=/1200x628/smart/filters:quality(80)/cloudfront-us-east-2.images.arcpublishing.com/reuters/4BPRNBPSYJMJZL5OH7MMETNYM4.jpg",
          "url": "https://www.reuters.com/world/china-hopes-france-can-help-take-heat-out-relations-with-eu-2023-07-29/",
          "publishedTime": 1690622421,
          "source": "reuters.com",
          "embeddings": [-0.06358712911605835, -0.001011253334581852, -0.012027012184262276]
      },
      {
         "title": "Japan names China its greatest strategic challenge",
          "description": "Japan sees China's growing ambition for power as its \"greatest strategic challenge,\" according to the new white paper on defence approved on Friday by the government of Japanese Prime Minister Fumio Kishida.",
          "uuid": "91bc847b-9e9d-497f-9de4-d22b219390be",
          "content": "TOKYO : Japan sees China's growing ambition for power as its \"greatest strategic challenge,\" according to the new white paper on def...",
  
  
          "thumbnailUrl": "https://www.reuters.com/resizer/Cr0DMOyD_IkT6hcOsRTU8xtbE5g=/1200x628/smart/filters:quality(80)/cloudfront-us-east-2.images.arcpublishing.com/reuters/RNAKI34TPRIRDNFWTIZYWDRUIA.jpg",
          "url": "https://www.reuters.com/business/aerospace-defense/china-us-boost-passenger-airline-flights-usdot-2023-05-03/",
          "publishedTime": 1683157315,
          "source": "reuters.com",
          "embeddings": [0.009848859161138536, -0.0479600615799427, 0.010806463658809662]
      }
  ]
  ```



**Embeddings**

- An *embedding* is a real-value vector that represents the semantic meaning of a piece of text. In our case, we use a 300-D vector of floats to represent the semantic meaning of each article, i.e. 300-D *article embeddings*.

- Our embeddings are generated using `all-MiniLM-L6-v2`, which provides a good balance between performance and hardware requirements/speed. 

- Each article's embedding is the weighted sum of the title's and description's embeddings. The weightage was empirically determined.

- All our embeddings are precomputed and saved in the fulltext search engine, ready to serve queries.



**Forming events from articles**

- When you send a query to readtimelines.com, our server first searches the fulltext search engine for relevant articles published recently.

- We take these articles and cluster their embeddings via an unsupervised learning algorithms ([OPTICS](https://en.wikipedia.org/wiki/OPTICS_algorithm)), with a sliding window.

- The articles within a cluster are semantically related, hence they are likely describing the same events. We prune the junk clusters (clusters that don't represent an independent event), and serve the rest as *events*. 

- These events are then sorted chronologically to form a *timeline*: this is what you queried for!
  
  ```json
  {
      "events": [
          {
              "name": "France's Le Maire presses China on market access and lobbies for electric car investment",
              "date": "2023-07-30",
              "articles": [
                  {
                      "title": "China hopes France can help take heat out of relations with EU",
                      "url": "https://www.reuters.com/world/china-hopes-france-can-help-take-heat-out-relations-with-eu-2023-07-29/",
                      "thumbnail_url": "https://www.reuters.com/resizer/HJFF_pY0mp8L296eXv2plFEmbps=/1200x628/smart/filters:quality(80)/cloudfront-us-east-2.images.arcpublishing.com/reuters/4BPRNBPSYJMJZL5OH7MMETNYM4.jpg",
                      "date_published": "2023-07-29T09:20:21",
                      "snippet": "China hopes France can \"stabilise the tone\" of EU-China relations, vice-premier He Lifeng told his French counterpart in Beijing on Saturday, as European leaders debate how balance \"de-risking\" and cooperating with the world's second-largest economy."
                  },
                  {
                      "title": "France's Le Maire presses China on market access and lobbies for electric car investment",
                      "url": "https://www.washingtonpost.com/business/2023/07/30/china-france-ukraine-trade-technology-electric-cars/f2ad27ec-2e9b-11ee-a948-a5b8a9b62d84_story.html",
                      "thumbnail_url": "https://www.washingtonpost.com/wp-apps/imrs.php?src=https://arc-anglerfish-washpost-prod-washpost.s3.amazonaws.com/public/5YDKIUROTMI65KKIUW4KTNRNQQ_size-normalized.jpg&w=1440",
                      "date_published": "2023-07-30T05:43:02",
                      "snippet": "The French finance minister says he pressed Chinese leaders to open their markets wider to foreign companies"
                  }
              ]
          },
          {
              "name": "Foreign ships, aircraft in East and South China Seas escalating tensions: China's defence ministry",
              "date": "2023-07-29",
              "articles": [
                  {
                      "title": "Japan names China its greatest strategic challenge",
                      "url": "https://www.thestar.com.my/aseanplus/aseanplus-news/2023/07/29/japan-names-china-its-greatest-strategic-challenge",
                      "thumbnail_url": "https://apicms.thestar.com.my/uploads/images/2023/07/29/2202963.jpg",
                      "date_published": "2023-07-29T15:23:00",
                      "snippet": "Japan sees China's growing ambition for power as its \"greatest strategic challenge,\" according to the new white paper on defence approved on Friday by the government of Japanese Prime Minister Fumio Kishida."
                  },
                  {
                      "title": "Foreign ships, aircraft in East and South China Seas escalating tensions: China's defence ministry",
                      "url": "https://www.straitstimes.com/asia/east-asia/foreign-ships-aircraft-in-east-and-south-china-seas-escalating-tensions-chinas-defence-ministry",
                      "thumbnail_url": "https://static1.straitstimes.com.sg/s3fs-public/styles/large30x20/public/articles/2023/07/29/IMGsea11623C77K.jpg",
                      "date_published": "2023-07-29T05:17:00",
                      "snippet": "In Japan's annual defence paper, it offered a gloomy assessment of the threat of China’s territorial ambitions. Read more at straitstimes.com."
                  }
              ]
          }
      ]
  }
  ```



**Making it fast, cheap, and reliable**

- Serverless wasn't an option — we had to choose between dealing with weak CPUs, cold starts, or high prices

- We decided to run the backend on a Digital Ocean droplet, which is moderately powerful at a low price. To save on cost, the droplet is shared with the data pipeline, and pm2 is used to manage the processes.

- Overall, the total cost for running a ~100k article fulltext search engine + data pipeline + API with ML inference is around 25 USD. Pretty good!






