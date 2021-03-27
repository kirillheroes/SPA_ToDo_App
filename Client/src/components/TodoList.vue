<template>
    <div>
        <ul id="todo-list">
            <TodoItem
                v-for="todo of todos"
                v-bind:todo="todo"
            />
        </ul>
    </div>
</template>

<script>
    import TodoItem from '@/components/TodoItem'
    export default {
        name: "TodoList",
        props: ['todos'],
        components: {
            TodoItem
        }
    }
</script>

<style>
    ul {
        list-style: none;
        margin: 0;
        padding: 0;
    }

</style>