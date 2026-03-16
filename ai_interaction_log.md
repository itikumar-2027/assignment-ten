#I started by using codex to help with the setup process, which took a long while. The environment setup was easy, but there were some issues with GitHub. We tried two ways to fix this (install GitHub CLI and Personal ACccess Token) and eventually option 1 worked. 

#Then, we tried the first prompt of Hello! into the chatbot to see if it worked but it posed an error: API error 403: {"error":"This authentication method does not have sufficient permissions to call Inference Providers on behalf of user aditiiiiiikumar"}

#I went into Hugging Face and updated the permissions of my token to include inferences. Now, I start the actual tasks: 

# Task 1: perfect. that works. let's move into task 1. Build the foundational ChatGPT-style app in four progressive stages. Complete each part before moving to the next — each part extends the previous one.

The diagram below shows the expected layout your app should match. Your implementation does not need to be pixel-perfect, but all elements must appear in the correct locations.

we'll go step by step within task 1, but pls familiarize yourself with the picture [inserted the picture]
# Alright, here is Part 2: Part B: Multi-Turn Conversation UI (30 points)
Requirements:

Extend Part A to replace the hardcoded test message with a real input interface.
Use native Streamlit chat UI elements. Render messages with st.chat_message(...) and collect user input with st.chat_input(...).
Add a fixed input bar at the bottom of the main area.
Store the full conversation history in st.session_state. After each exchange, append both the user message and the assistant response to the history.
Send the full message history with each API request so the model maintains context.
Render the conversation history above the input bar using default Streamlit UI elements rather than CSS-based custom chat bubbles.
The message history must scroll independently of the input bar — the input bar stays visible at all times.
Success criteria (Part B): Sending multiple messages in a row produces context-aware replies (e.g. the model remembers the user’s name from an earlier message). Messages are displayed with correct styling and the input bar remains fixed.

#Added a picture of the expected UI, "this should be the current look"

#Alright, let's do Part C:: Part C: Chat Management (25 points)
Requirements:

Add a New Chat button to the sidebar that creates a fresh, empty conversation and adds it to the sidebar chat list.
Use the native Streamlit sidebar (st.sidebar) for chat navigation.
The sidebar shows a scrollable list of all current chats, each displaying a title and timestamp.
The currently active chat must be visually highlighted in the sidebar.
Clicking a chat in the sidebar switches to it without deleting or overwriting any other chats.
Each chat entry must have a ✕ delete button. Clicking it removes the chat from the list. If the deleted chat was active, the app must switch to another chat or show an empty state.
Success criteria (Part C): Multiple chats can be created, switched between, and deleted independently. The active chat is always visually distinct.

#codex said this: est checklist:

Create 2–3 chats with New Chat.
Send different messages in each.
Switch between chats and confirm history persists.
Delete a chat and confirm it disappears and active selection updates.
Tell me the results and we’ll proceed to Part D.

# I was confused: what does 4 mean ? i deleted a chat and it disappeared it from the sidebar 

#It worked, moving to part D:ok, that works. let's do Part D: Part D: Chat Persistence (25 points)
Requirements:

Each chat session is saved as a separate JSON file inside a chats/ directory. Each file must store at minimum: a chat ID, a title or timestamp, and the full message history.
On app startup, all existing files in chats/ are loaded and shown in the sidebar automatically.
Returning to a previous chat and continuing the conversation must work correctly.
Deleting a chat (✕ button) must also delete the corresponding JSON file from chats/.
A generated or summarized chat title is acceptable and encouraged. The title does not need to be identical to the first user message.
Success criteria (Part D): Closing and reopening the app shows all previous chats intact in the sidebar. Continuing a loaded chat works correctly. Deleting a chat removes its file from disk.


#yup, that works. i'm confused about what gets saved in memory.json file ?

# Task 2: Great! Let's move into Task 2: Response Streaming (20 points)
Goal: Display the model’s reply token-by-token as it is generated instead of waiting for the full response.

Requirements
Use the stream=True parameter in your API request and handle the server-sent event stream.
In Streamlit, use native Streamlit methods such as st.write_stream() or manually update a placeholder with st.empty() as chunks arrive.
The full streamed response must be saved to the chat history once streaming is complete.
Hint: Add stream=True to your request payload and set stream=True on the requests.post() call. The response body will be a series of data: lines in SSE format.

Note: Very small models such as meta-llama/Llama-3.2-1B-Instruct may stream so quickly that the output appears to arrive all at once. If your app is correctly receiving multiple streamed chunks but the effect is too fast to notice, you are required to add a very short delay between rendering chunks so the streaming behavior is visible in the UI.

Success criteria: Responses appear incrementally in the chat interface and are correctly saved to history.

# I asked: what does it mean to appear incrementally ?

#Task 3: Here is TASK 3: Task 3: User Memory (20 points)
Goal: Extract and store user preferences from conversations, then use them to personalize future responses.

Requirements
After each assistant response, make a second lightweight API call asking the model to extract any personal traits or preferences mentioned by the user in that message.
Extracted traits are stored in a memory.json file. Example categories might include name, preferred language, interests, communication style, favorite topics, or other useful personal preferences.
The sidebar displays a User Memory expander panel showing the currently stored traits.
Include a native Streamlit control to clear/reset the saved memory.
Stored memory is injected into the system prompt of future conversations so the model can personalize responses.
Implementation note: The categories above are only examples for reference. It is up to you to decide what traits to store, how to structure your memory.json, how to merge or update existing memory, and how to incorporate that memory into future prompts, as long as the final app clearly demonstrates persistent user memory and personalization.

Hint: A simple memory extraction prompt might look like: “Given this user message, extract any personal facts or preferences as a JSON object. If none, return {}”

Success criteria: User traits are extracted, displayed in the sidebar, and used to personalize subsequent responses.



i want to include ALL categories mentioned above

# I tested this by saying the following sentences: “My name is Aditi. I like hiking and food. I prefer concise answers, "What should I do this weekend"

#that does work, but i'm still a tad confused about what should appear in memory.json --> learned that when the memory is cleared, json is ALSO cleared. didn't realize this before. 