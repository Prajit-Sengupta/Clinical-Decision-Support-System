function fetchTuberculosisNews() {
    const apiKey = '9b73ba5caee5441d955195c40608913d';
    const newsUrl = `https://newsapi.org/v2/everything?q=tuberculosis&apiKey=${apiKey}`;
  
    fetch(newsUrl)
      .then(response => response.json())
      .then(data => {
        const carouselInner = document.querySelector('.carousel-inner');
  
        if (data.status === 'ok') {
          const articles = data.articles;
  
          articles.forEach((article, index) => {
            const newsItem = document.createElement('div');
            newsItem.classList.add('carousel-item');
            if (index === 0) {
              newsItem.classList.add('active');
            }
  
            const newsTitle = document.createElement('h2');
            newsTitle.textContent = article.title;
  
            const newsDescription = document.createElement('p');
            newsDescription.textContent = article.description;
  
            newsItem.appendChild(newsTitle);
            newsItem.appendChild(newsDescription);
            carouselInner.appendChild(newsItem);
          });
        } else {
          const errorMessage = document.createElement('p');
          errorMessage.textContent = 'Failed to fetch news.';
          carouselInner.appendChild(errorMessage);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        const carouselInner = document.querySelector('.carousel-inner');
        const errorMessage = document.createElement('p');
        errorMessage.textContent = 'An error occurred while fetching news.';
        carouselInner.appendChild(errorMessage);
      });
  }
  
  fetchTuberculosisNews();
