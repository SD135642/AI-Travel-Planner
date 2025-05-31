from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
from werkzeug.utils import secure_filename
app = Flask(__name__)

#for gpt
import os
from openai import OpenAI

import openai_secrets

client = OpenAI(api_key=openai_secrets.SECRET_KEY)


@app.route('/')
def index():
    return render_template('landing-page.html') 

@app.route('/plan')
def plan():
    return render_template('plan.html') 

@app.route('/prepare')
def prepare():
    return render_template('prepare.html') 

@app.route('/submit_activities', methods=['GET', 'POST'])
def submit_activities():
    city = request.form.get('destination')
    dates = request.form.get('dates')

    # Collect checkbox data (activities)
    activities = request.form.getlist('activities')

    #print("DATES  are " + str(dates))
    #print(" CITY is " + str(city))
    #print(" ACT'S are " + str(activities))


    data = {
        'city': city,
        'dates': dates,
        'activities': activities
    }
    
  
    itinerary = str(get_gpt_response_itinerary(data))
    return render_template('planning.html', itinerary=itinerary)


@app.route('/submit_data', methods=['GET', 'POST'])
def submit_data():
    airline = request.form.get('airline')
    airports = request.form.get('airports')
    citizenship = request.form.get('citizenship')
    hotel = request.form.get('hotel')
    activities = request.form.getlist('activities')

    print("airline is " + str(airline))
    print(" airports is " + str(airports))
    print(" citizenship is " + str(citizenship))
    print(" hotel is " + str(hotel))
    print(" activities are " + str(activities))

    data = {
        'airline': airline,
        'airports': airports,
        'citizenship': citizenship,
        'hotel': hotel,
        'activities': activities
    }
  
    itinerary = str(get_gpt_response_data(data))
    return render_template('preparing.html', itinerary=itinerary)





def parse_answers_from_gpt_response(keyword_response):    
    keyword_list = keyword_response.split("\n\n")
    new_keyword_list = []

    for item in keyword_list:
        # Strip leading/trailing spaces from each item
        item = item.strip()

        # If item is not empty, process it further
        if item.strip():
            # Optional: Remove leading number followed by dot (e.g., "1. Answer" -> "Answer")
            if "." in item:
                item = item[item.index(".") + 1:].strip()

            # Append the cleaned item to the new list
            new_keyword_list.append(item)

    return new_keyword_list

def get_gpt_response_itinerary(data):
    dates = data.get('dates')
    city = data.get('city')
    activities = data.get('activities')
    print(" dates are " + str(dates))
    print(" city is " + str(city))
    print(" activities are " + str(activities))

    prompt = (f"Give a full, detailed itinerary (including prices, best time to visit, how to get there, and more) for "
              f"the following city: "+city+" for these dates: "+dates+". Here are the activities the user prefers: "+', '.join(activities)+"Keep "
              f"in mind the usual weather and the season in your recommendations. Do not include anything else in your answer. "
              f"except for the itinerary. Try to be as specific as possible so that the user has to do minimal to no research. "
              f"IMPORTANT: ADD 5 POUND SIGNS (like this:#####) before each day's header for easier parsing later. Do not include anything else in your "
              f"response, just the itinerary!"
            )
    response_raw = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
        {
          "role": "user",
          "content": prompt
        }
      ],
      # temperature=0,
      #max_tokens=100,
      # top_p=1,
      # frequency_penalty=0,
      # presence_penalty=0
    )

    response = response_raw.choices[0].message.content  
    return response

def get_gpt_response_data(data):
    airline = data.get('airline')
    airports = data.get('airports')
    citizenship = data.get('citizenship')
    hotel = data.get('hotel')
    activities = data.get('activities')

    prompt = (f"You are a helpful personal travel assistant. Your goal is to minimize the research the user has to do. "
              f"Provide this information in detail: "+', '.join(activities)+". "
              f"Follow this structure for your response but OMIT ANY INFORMATION YOU WERE NOT ASKED ABOUT! "
              f"I will give you hints on everything but you should Only return the responses you were asked for. This airline "+airline+" policies and restrictions. Then, " 
              f"provide the data on the following airport "+airports+" including detailed ways how to get from there "
              f"to the hotel "+hotel+" (include exact subway/train lines, ticket prices, time estimate, price estimate "
              f"for taxi, etc ), how crowded it usually is, recommendations on how early to arrive in respect to average  "
              f" wait time, where to eat there, what terminal the airline operates from, and any other current alerts/relevant info. "
              f"Also provide a detailed document checklist for flying into the mentioned airport in respect to "+citizenship+" citizenship. "
              f"IMPORTANT: Start every section with 5 pound signs (like this: ##### before each section's header for easier parsing later. "
              f"Your goal is to do all the research for the user and give them detailed, ready-to-go options so "
              f"that they have to do minimal to no research. Include links where appropriate. Do not include "
              f"anything else in your response, just the answers. Try to be as specific as possible and make some "
              f"basic choices/assumptions if needed for the user. First line should be the header of the respective section. "
            )


    response_raw = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
        {
          "role": "user",
          "content": prompt
        }
      ],
      # temperature=0,
      #max_tokens=100,
      # top_p=1,
      # frequency_penalty=0,
      # presence_penalty=0
    )

    response = response_raw.choices[0].message.content 

    return response



if __name__ == '__main__':
    app.run(debug=True)
