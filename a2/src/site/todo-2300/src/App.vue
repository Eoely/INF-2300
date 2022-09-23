
<template>
  <header>
    <h1>'TODO'</h1>
  </header>

  <body>
    <div class="container">
      <div class="addnew">
        <input type="button" value="Confirm" @click="appendTask">
        <input v-model="newTaskName">
      </div>
      <div class="rest">
        <input type="button" value="delete all" @click="deleteAllTasks">
        <ul style="list-style-type:none">
          <li v-for="task in tasks" class="todoitem">
            <input type="button" class="deletebutton" value="X" @click="deleteTask(task.id)">
            <input type="button" :value="task.done ? 'Undo' : 'Complete'" @click="completeTask(task.id)">
            <input type="button" value="Edit" @click="updateTaskName(task.id)">
            <input v-model="task.name" :class="{completedTask: task.done}" @change="testfunc()">
          </li>
        </ul>
      </div>
    </div>
  </body>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import axios from 'axios'

type Task = {
  "done": boolean,
  "id": number,
  "name": string,
};

const tasks = ref<Task[]>([]);
const isAddingNew = ref(false);
const newTaskName = ref('')

const getTasks = () => axios.get('http://127.0.0.1:5000/api/items/').then(response => tasks.value = response.data["items"]);

onMounted(getTasks);

const showAddTask = () => isAddingNew.value = !isAddingNew.value;

const testfunc = () => console.log('this is a test');


const deleteTask = async (id: number) => {
  await axios.delete(`http://127.0.0.1:5000/api/items/${id}`)
    .then(response => console.log('delres', response.data))
    .catch(error => console.log('delerr', error));

  getTasks();
}

const completeTask = async (id: number) => {
  let task = tasks.value.find(t => t.id == id);

  if (task) {
    task.done = !task.done;
    console.log('task complete', task);

    await axios.put(`http://127.0.0.1:5000/api/items/${id}`, task)
      .then(response => console.log('putres', response))
      .catch(error => console.log('puterr', error));

    getTasks();
  } else {
    console.error('No task with that id was found');
  }

}

const updateTaskName = async (id: number) => {
  let task = tasks.value.find(t => t.id == id);
  await axios.put(`http://127.0.0.1:5000/api/items/${id}`, task)
    .then(response => console.log('putres', response))
    .catch(error => console.log('puterr', error));

  getTasks();

}

const deleteAllTasks = async () => {
  const reqs = tasks.value.map(task => axios.delete(`http://127.0.0.1:5000/api/items/${task.id}`));
  //TODO: Handle errors.
  await axios.all(reqs)
    .then(data => console.log('deldata', data))
    .catch(error => console.log('delallerr', error));

  getTasks();

}

const appendTask = async () => {
  const newTask = {
    "name": newTaskName.value,
  }

  await axios.post('http://127.0.0.1:5000/api/items/', newTask)
    .then(response => console.log(response.data.item))
    .catch(error => console.error(error))

  newTaskName.value = '';
  isAddingNew.value = false;

  //Could also just append response to tasks array
  getTasks();
};

</script>


<style scoped>
/* header {
  line-height: 1.5;
} */

.completedTask {
  background-color: green;
}

.container {
  border: 0.05em solid red;
  position: relative;
  margin: 1rem;

}

.todoitem {
  position: absolute;
  width: 100%;
  height: 100vh;
}

.deletebutton {
  background-color: red
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  /* .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  } */
}
</style>
