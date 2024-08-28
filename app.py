from flask import Flask, render_template, jsonify, request
from bs4 import BeautifulSoup
import requests
import markdown2
import google.generativeai as genai
from dateutil import parser

app = Flask(__name__)

def search_gemini(query):
    genai.configure(api_key="AIzaSyC4RDV6Yv25xaxB_NZ4bJY2p41aQEHuWwY")

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(f"{query} Please explain the following article that capture the essence of the content while maintaining key information and context and rewrite in brief in more than 200 words with no html tags and proper spacing and endings in between lines. Ensure clarity and readability for a general audience.")
    cleaned_text = response.text
    html_text = markdown2.markdown(cleaned_text)
    return html_text

def extract_news(url, query=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    news_items = []
    max_news_items = 5  # Set the maximum number of news items to fetch
    news_counter = 0

    if soup.find('div', class_='category-col'):
        for article in soup.find_all('div', class_='category-col'):
            if news_counter >= max_news_items:  # Check if the limit is reached
              break
            title_tag = article.find('h3')
            title = title_tag.get_text(strip=True) if title_tag else "No title available"

            # Extract the news link from the 'href' attribute in the anchor tag
            link_tag = title_tag.find_parent('a') if title_tag else None
            link = link_tag['href'] if link_tag else "No link available"
            if link_tag:
                response = requests.get(link)
                soup = BeautifulSoup(response.content, 'html.parser')
                inner_title = soup.find('h1', class_='story-title').get_text(strip=True) if soup.find('h1', class_='story-title') else "No inner title available"
                subcap = soup.find('p', class_='subcap-story').get_text(strip=True) if soup.find('p', class_='subcap-story') else "No subcap available"
                time = soup.find('div', class_='story-dec-time').get_text(strip=True) if soup.find('div', class_='story-dec-time') else "No time available"
                inner_image_tag = soup.find('img', class_='w-100 story-hero-img')
                image1 = inner_image_tag['src'] if inner_image_tag else "https://via.placeholder.com/150"
                
                # Extract the paragraph from the `sb-text` div
                if soup.find('div', class_='sb-card'):
                   paragraph=''
                   for in_article in soup.find_all('div', class_='sb-card'):
                    for content_tag in in_article.find_all('p'):
                     paragraph = paragraph + content_tag.get_text(strip=True)



                #for in_article in soup.find_all('div', class_='sb-text'):
                # paragraph = in_article.find('p').get_text(strip=True) if sb_text_div and sb_text_div.find('p') else "No additional content available"
            else:
                inner_title = ""
                subcap = ""
                time = ""
                image1 = "https://via.placeholder.com/150"
                paragraph = "No additional content available"

            # Extract image source from the <img> tag
            image_tag = article.find('img', class_='article-img')
            image = image_tag['src'] if image_tag else "https://via.placeholder.com/150"

            # Extract the author from the <span> tag with class 'name'
            author_tag = article.find('span', class_='name')
            author = author_tag.get_text(strip=True) if author_tag else "No author available"

            # Extract the category (slug) from the <div> tag with class 'slug'
            category_tag = article.find('div', class_='slug')
            category = category_tag.get_text(strip=True) if category_tag else "No category available"

            # Use title for description if no specific description is available
            description = title

            # Append the extracted data to the news_items list
            news_items.append({
                'title': title,
                'inner_title': inner_title,
                'subcap': subcap,
                'time': time,
                'link': link,
                'description': description,
                'image': image,
                'innerimg': image1,
                'author': author,
                'category': category,
                'paragraph': search_gemini(paragraph)  # Newly added field
            })
            news_counter+=1

    else:
        filtered_news_items = []
        for article in soup.find_all('div', class_='col-12 col-md-3 col-lg-3 mb-3 br-grey'):
            if news_counter >= max_news_items:  # Check if the limit is reached
              break
            title_tag = article.find('h3')
            title = title_tag.get_text(strip=True) if title_tag else "No title available"

            # Extract the news link from the 'href' attribute in the anchor tag
            link_tag = title_tag.find_parent('a') if title_tag else None
            link = link_tag['href'] if link_tag else "No link available"
            if link_tag:
                response = requests.get(link)
                soup = BeautifulSoup(response.content, 'html.parser')
                inner_title = soup.find('h1', class_='story-title').get_text(strip=True) if soup.find('h1', class_='story-title') else "No inner title available"
                subcap = soup.find('p', class_='subcap-story').get_text(strip=True) if soup.find('p', class_='subcap-story') else "No subcap available"
                time = soup.find('div', class_='story-dec-time').get_text(strip=True) if soup.find('div', class_='story-dec-time') else "No time available"
                inner_image_tag = soup.find('img', class_='w-100 story-hero-img')
                image1 = inner_image_tag['src'] if inner_image_tag else "https://via.placeholder.com/150"
                
                # Extract the paragraph from the `sb-text` div
                if soup.find('div', class_='sb-card'):
                   paragraph=''
                   for in_article in soup.find_all('div', class_='sb-card'):
                    for content_tag in in_article.find_all('p'):
                     paragraph = paragraph + content_tag.get_text(strip=True)

            else:
                inner_title = ""
                subcap = ""
                time = ""
                image1 = "https://via.placeholder.com/150"
                paragraph = "No additional content available"

            # Extract image source from the <img> tag
            image_tag = article.find('img', class_='article-img')
            image = image_tag['src'] if image_tag else "https://via.placeholder.com/150"

            # Extract the author from the <span> tag with class 'name'
            author_tag = article.find('span', class_='name')
            author = author_tag.get_text(strip=True) if author_tag else "No author available"

            # Extract the category (slug) from the <div> tag with class 'slug'
            category_tag = article.find('div', class_='slug')
            category = category_tag.get_text(strip=True) if category_tag else "No category available"

            # Use title for description if no specific description is available
            description = title

            # Append the extracted data to the news_items list
            news_items.append({
                'title': title,
                'link': link,
                'subcap': subcap,
                'time': time,
                'inner_title': inner_title,
                'description': description,
                'image': image,
                'innerimg': image1,
                'author': author,
                'category': category,
                'paragraph': search_gemini(paragraph)  # Newly added field
            })
            if query:
              if any(query.lower() in str(value).lower() for value in news_items.values()):
                   filtered_news_items.append(news_items)
              else:
                   filtered_news_items.append(news_items)

            news_counter += 1


    try:
        news_items.sort(key=lambda x: parser.parse(x['time']), reverse=True)
    except Exception as e:
        print(f"Error sorting news items by date: {e}")

    return news_items

def extract_news_by_query(query):
    # This function fetches all news and filters them by query keyword.
    all_news_items = []  # Initialize a list to hold all news items

    # Example of fetching and combining multiple categories
    categories = ['cricket', 'football', 'hockey', 'badminton', 'paris-olympic-games-2024', 'tennis', 'motorsport']
    for category in categories:
        url = f"https://www.outlookindia.com/sports/{category}"
        news_items = extract_news(url)
        all_news_items.extend(news_items)  # Combine all news items from different categories

    # Filter news items by the search query
    filtered_news = [item for item in all_news_items if query.lower() in item['title'].lower() or query.lower() in item['paragraph'].lower()]

    return filtered_news

@app.route('/news/<category>')
def news(category):
    # Construct the URL dynamically based on the category parameter
    url = f"https://www.outlookindia.com/sports/{category}"
    news_items = extract_news(url)
    query = request.args.get('query', '')

    news_items = extract_news(url, query=query)  # Pass query to extract_news
    # Return JSON data instead of rendering a template
    return jsonify(news_items)
@app.route('/search')

def search():
    query = request.args.get('query')
    if not query:
        return jsonify([])

    # Implement your logic to fetch and filter news items based on the query
    news_items = extract_news_by_query(query)
    
    return jsonify(news_items)

if __name__ == "__main__":
    app.run(debug=True)
