from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from openai import OpenAI

client = OpenAI(api_key="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")
from googleapiclient.discovery import build
import re
class ChatView(View):

    def get(self, request):
        if request.GET.get('val'):

            models = client.models.list()

            # Use GPT-3.5-turbo to get the chat completion response
            chat_completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": request.GET.get('val')}])

            message = chat_completion.choices[0].message.content

            # Check if the user's query contains keywords related to YouTube
            youtube_results = ""
            if re.search(r'\b(?:youtube|videos?)\b', request.GET.get('val'), re.IGNORECASE):
                youtube_results = self.get_youtube_suggestions(request.GET.get('val'))
                if youtube_results:
                    message += "\n\nYouTube Suggestions:\n" + youtube_results

            # Return JSON response with the generated message
            return JsonResponse({'message': message, 'youtube_suggestions': youtube_results})

        return render(request, 'index.html')

    def get_youtube_suggestions(self, query):
        # Replace 'YOUR_YOUTUBE_API_KEY' with your actual YouTube API key
        youtube = build('youtube', 'v3', developerKey='AIzaSyAUeM1xIlUQgaJpxNClDGAGQpLCw25F8uM')

        # Perform a YouTube search based on the user's query
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=5  # You can adjust the number of results you want to show
        ).execute()

        # Extract video titles and URLs from the search results
        youtube_results = ""
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                title = search_result['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={search_result['id']['videoId']}"
                youtube_results += f"<a href='{video_url}' target='_blank'>{title}</a><br>"

        return youtube_results

    def convert_message_to_html(self, message):
        # Convert newlines to <br> tags and convert URLs to clickable links
        message = message.replace('\n', '<br>')
        message = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', message)
        return message
