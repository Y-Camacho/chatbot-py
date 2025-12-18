<template>
  <!-- Chatbot Container -->
  <transition name="chatbot-fade-scale">
    <div v-if="isOpen" class="chatbot-container">
      <div class="chatbot-header">
        <h2>ChatBot</h2>
        <button class="close-button" @click="toggleChat">X</button>
      </div>

      <div class="chatbot-body">
        <div class="messages" ref="chatBody">
          <div
            v-for="message in messages"
            :key="message.id"
            :class="['message', message.type === 'response' ? 'mss-response' : 'mss-question']"
          >
            {{ message.text }}
          </div>

          <!-- Loading spinner -->
          <div v-if="loading" class="message mss-response loading">
            <span class="spinner"></span> Escribiendo...
          </div>
        </div>

        <div class="input-area">
          <input v-model="inputQuestion" type="text" placeholder="Type your question ..." @keyup.enter="doQuestion(inputQuestion)" />
          <button @click="doQuestion(inputQuestion)">Send</button>
        </div>
      </div>
    </div>
  </transition>

  <!-- Chatbot Circle -->
  <transition name="chatbot-fade-scale">
    <div v-if="!isOpen" class="chatbot-circle" @click="toggleChat">
      <img :src="icon" alt="ChatBot Icon">
    </div>
  </transition>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import icon from '@/assets/chatbot-icon.png'

const isOpen = ref(false)
const loading = ref(false)
const inputQuestion = ref('')
const messages = ref([
  { id: "d-1", type: 'response', text: 'Hola! Cómo puedo ayudarte hoy?' }
])

const chatBody = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBody.value) {
      chatBody.value.scrollTop = chatBody.value.scrollHeight
    }
  })
}

const doQuestion = async (question) => {
  if (!question.trim()) return

  // Agregar pregunta inmediatamente
  const questionId = `q-${Date.now()}`
  messages.value.push({ id: questionId, type: 'question', text: question })
  scrollToBottom()
  inputQuestion.value = ''

  // Mostrar loading
  loading.value = true

  try {
    const res = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    })
    const data = await res.json()

    // Agregar respuesta
    messages.value.push({ id: `r-${data.id}`, type: 'response', text: data.answer })
    scrollToBottom()
  } catch (error) {
    messages.value.push({ id: `r-error-${Date.now()}`, type: 'response', text: 'Ocurrió un error. Intenta de nuevo.' })
    scrollToBottom()
  } finally {
    loading.value = false
  }
}

const toggleChat = () => {
  isOpen.value = !isOpen.value
}
</script>



<style>
.chatbot-container {
  position: fixed;
  bottom: 20px;
  right: 20px;

  width: 350px;
  height: 500px;

  background-color: #fff;
  border: solid 5px #333;
  border-radius: 10px;
  box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px;
}

.chatbot-header {
  background-color: #333;
  color: white;
  padding: 15px;

  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-button {
  background: none;
  
  display: flex;
  align-items: center;
  justify-content: center;
  
  width: 25px;
  height: 25px;
  
  border-radius: 50%;

  color: white;
  font-weight: bold;

  font-size: 12px;
  cursor: pointer;
}

.close-button:hover {
  color: #333;
  background-color: white;

  border: solid 1px #333;
}

.chatbot-body {
  padding: 15px;

  height: calc(100% - 60px) ;
  
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;

  display: flex;
  flex-direction: column;

  height: 100%;
  overflow-y: auto;
  margin-bottom: 10px;
}

.message {

  width: 70%;

  color: #333;

  padding: 10px;
  margin-bottom: 10px;
  border-radius: 5px;

}

.mss-response {
  background-color: #f4f5ae;
  align-self: flex-start;
}

.mss-question {
  background-color: #b5f0bf;
  align-self: flex-end;
}

.input-area {
  display: flex;
  gap: 10px;
}

.input-area input {
  flex: 1;

  padding: 10px;

  border: 1px solid #ccc;
  outline: none;
  border-radius: 20px;
}

.input-area button {
  padding: 10px 20px;
  background-color: #333;
  
  color: white;
  font-weight: bold;

  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.input-area button:hover {
  background-color: #555;
}

/* ChatBot Circle */

.chatbot-circle {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 80px;
  height: 80px;
  background-color: #333;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  box-shadow: rgb(114, 179, 0) 0px 7px 29px 0px;

  animation: pulseScale 2s ease-in-out infinite;

  cursor: pointer;
}

.chatbot-circle img {
  width: 100%;
  height: 100%;
}

@keyframes pulseScale {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1); /* +10% */
  }
  100% {
    transform: scale(1);
  }
}

/* Transición chatbot */

.chatbot-fade-scale-enter-active,
.chatbot-fade-scale-leave-active {
  transition: all 0.3s ease;
}

.chatbot-fade-scale-enter-from,
.chatbot-fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

.chatbot-fade-scale-enter-to,
.chatbot-fade-scale-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}

/* Spinner para loading */
.loading {
  display: flex;
  align-items: center;
  gap: 10px;
  font-style: italic;
  color: #555;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ccc;
  border-top-color: #333;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

</style>