// script.js
function processImage() {
    const input = document.getElementById('imageFileInput');
    const file = input.files[0];
  
    if (file) {
      const formData = new FormData();
      formData.append('image', file);
  
      fetch('/process', {
        method: 'POST',
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          const outputDiv = document.getElementById('output');
          outputDiv.textContent = data.result;
        })
        .catch((error) => {
          console.log('Error:', error);
        });
    } else {
      console.log('No image file selected');
    }
  }

  function fetchTuberculosisNews() {
    const apiKey = '9b73ba5caee5441d955195c40608913d';
    const newsUrl = 'https://newsapi.org/v2/everything?q=tuberculosis+doctors&language=en&apiKey=' + apiKey;
  
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


  function setupInformationWindow() {
    const informationButton = document.querySelector('.information-button');
    const informationWindow = document.getElementById('informationWindow');
    const closeButton = document.getElementById('closeButton');

    function showInformationWindow() {
        informationWindow.classList.add('relative');
        informationWindow.style.display = 'block';
    }

    function hideInformationWindow() {
        informationWindow.classList.remove('relative');
        informationWindow.style.display = 'none';
    }

    informationButton.addEventListener('click', showInformationWindow);
    closeButton.addEventListener('click', hideInformationWindow);

    // Hide the information window when clicked outside of it
    window.addEventListener('click', (event) => {
        if (!informationWindow.contains(event.target) && event.target !== informationButton) {
            hideInformationWindow();
        }
    });
}

// Call the setup function when the DOM is ready
document.addEventListener('DOMContentLoaded', setupInformationWindow);

