import { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

function App() {
  type Task = {
    done: boolean;
    id: number;
    name: string;
  };

  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTaskName, setNewTaskName] = useState<string>('');
  const api_url = "http://127.0.0.1:5000/api/items/";

  useEffect(() => {
    getTasks();
  }, []);

  const getTasks = async () => {
    const result = await axios.get(api_url);
    setTasks(result.data["items"]);
  };

  const deleteAllTasks = () => {
    const requests = tasks.map((task) => axios.delete(`${api_url}${task.id}`));

    axios
      .all(requests)
      .then(getTasks)
      .catch((error) => console.log(error.request.response));
  };

  const deleteTask = (id: number) => {
    console.log("deleting task", id);
    axios
      .delete(`${api_url}${id}`)
      .then(getTasks)
      .catch((error) => console.log(error.request.response));
  };

  const completeTask = (id: number) => {
    console.log("completing task", id);

    const task = tasks.find((t) => t.id === id);
    let updatedTask = { ...task };
    updatedTask.done = !updatedTask.done;
    axios
      .put(`${api_url}${id}`, updatedTask)
      .then(getTasks)
      .catch((error) => console.log(error.request.response));
  };

  const updateTaskName = (id: number, event: any) => {
    const newValue = event.target.value;
    const task = tasks.find((t) => t.id === id);

    if (task) {
      task.name = newValue;
      axios
        .put(`${api_url}${id}`, task)
        .then(getTasks)
        .catch((error) => console.log(error.request.response));
    }
  };

  const appendTask = () => {
    const newTask = {
      name: newTaskName,
    };
    
    axios
      .post(api_url, newTask)
      .then(getTasks)
      .catch((error) => console.log(error.request.response));
  };

  const taskList = tasks?.map((task, idx) => (
    <div key={idx} style={{ display: "flex" }}>
      <input
        defaultValue={task.name}
        onBlur={(event) => updateTaskName(task.id, event)}
      />
      <button onClick={() => deleteTask(task.id)}>Delete task</button>
      <button onClick={() => completeTask(task.id)}>Complete task</button>
      {task.done ? "completed" : "not completed"}
    </div>
  ));

  const newTaskInput = (
    <form onSubmit={appendTask}>
      <input placeholder={"new task"} value={newTaskName} onChange={(e) => setNewTaskName(e.target.value)}/>
      <input type="submit" value="Submit" />
    </form>
  );

  return (
    <div className="App">
      <h1>TODO INF-2300</h1>
      {newTaskInput}
      <button onClick={deleteAllTasks}>Delete all tasks</button>
      {taskList}
    </div>
  );
}

export default App;
