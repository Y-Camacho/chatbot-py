<template>
  <div class="page">
    <!-- Top Navbar -->
    <header class="navbar">
      <div class="nav-left">
        <img src="https://upload.wikimedia.org/wikipedia/commons/2/21/Nvidia_logo.svg" alt="NVIDIA" class="logo" />
        <nav class="nav-links">
          <a href="#">Productos</a>
          <a href="#">Soluciones</a>
          <a href="#">Sectores</a>
        </nav>
      </div>
      <div class="nav-right">
        <a href="#">Comprar</a>
        <a href="#">Controladores</a>
        <a href="#">Soporte</a>
        <a href="#">Sign In</a>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <span class="eyebrow">Centro de datos</span>
        <h1>
          Los fabricantes de modelos<br />
          aprovechan NVIDIA para la<br />
          próxima generación de<br />
          inteligencia
        </h1>
        <p>
          Desde GPT‑5.2 de OpenAI hasta los últimos modelos
          multimodales, los innovadores entrenan más rápido
          a escala con NVIDIA Blackwell y Hopper.
        </p>
        <button class="cta">Más información</button>
      </div>

      <div class="hero-image"></div>
    </section>

    <!-- Static carousel preview -->
    <section class="carousel">
      <div class="carousel-item active">
        <span class="category">Centro de datos</span>
        <p>Los fabricantes de modelos aprovechan NVIDIA…</p>
      </div>
      <div class="carousel-item">
        <span class="category">Inteligencia artificial</span>
        <p>Mezcla de expertos acelera 10 veces los principales…</p>
      </div>
      <div class="carousel-item">
        <span class="category">HPC</span>
        <p>Ver la charla Fireside Chat de NVIDIA SC25</p>
      </div>
    </section>

    <ChatBotComponent />
  </div>
</template>

<script setup>
import ChatBotComponent from './ChatBotComponent/ChatBotComponent.vue';

</script>

<style>
/* Reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: #000;
  color: #fff;
}

.page {
  width: 100%;
}

/* Navbar */
.navbar {
  height: 64px;
  background: #fff;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
}

.logo {
  height: 28px;
  margin-right: 24px;
}

.nav-left,
.nav-links,
.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-links a,
.nav-right a {
  text-decoration: none;
  color: #000;
  font-size: 14px;
}

/* Hero */
.hero {
  min-height: 600px;
  display: grid;
  grid-template-columns: 1.1fr 1fr;

  background-image: url("https://www.nvidia.com/content/dam/en-zz/Solutions/homepage/v2/mfg/worlds-leading-models-wmfg-offset-d.jpg");
  background-size: cover;
  background-position: center right;
}

.hero-content {
  padding: 96px 64px;
  z-index: 2;
}

.eyebrow {
  font-size: 14px;
  opacity: 0.8;
}

.hero h1 {
  font-size: 42px;
  line-height: 1.2;
  margin: 16px 0 24px;
}

.hero p {
  max-width: 520px;
  font-size: 16px;
  line-height: 1.6;
  opacity: 0.9;
  margin-bottom: 32px;
}

.cta {
  background: #76b900;
  color: #000;
  border: none;
  padding: 14px 24px;
  font-weight: 600;
  cursor: pointer;
}

/* Carousel Preview */
.carousel {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  padding: 32px 64px 64px;
  background: #000;
}

.carousel-item {
  border-top: 2px solid #333;
  padding-top: 16px;
  opacity: 0.5;
}

.carousel-item.active {
  opacity: 1;
  border-top-color: #76b900;
}

.category {
  display: block;
  font-size: 12px;
  margin-bottom: 8px;
  opacity: 0.7;
}

.carousel-item p {
  font-size: 14px;
}

@media (max-width: 1024px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .hero-image {
    height: 360px;
  }
}
</style>
