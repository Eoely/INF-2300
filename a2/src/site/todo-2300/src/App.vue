
<template>
  <header>
    <h1>'TODO'</h1>

  </header>
  <ul>
    <li v-for="task in tasks">
      <input type="checkbox" :value="task.name" :id="task.id"> {{task.name}}
    </li>
  </ul>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import HelloWorld from './components/HelloWorld.vue'
import axios from 'axios'

const tasks = ref<any>([]);
onMounted(() => axios.get('http://127.0.0.1:5000/api/items/').then(response => {tasks.value = response.data["items"]}));


</script>


<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
