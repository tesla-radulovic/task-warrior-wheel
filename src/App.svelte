<!-- App.svelte -->
<script lang="ts">
  import TimeWheel from './components/TimeWheel.svelte';
  import { v4 as uuidv4 } from 'uuid';

  type AgendaItem = {
    s_time: number,
    e_time: number,
    color: string,
    uuid: string,
  }

  let agenda_items: AgendaItem[] = [
    { s_time: 4, e_time: 6, color: 'blue', uuid: uuidv4() },
    { s_time: 8, e_time: 10, color: 'green', uuid: uuidv4() }
  ];

  const TASK_NAME_CHOICES: string[] = [
    'Deep Work',
    'Email Triage',
    'Standup Meeting',
    'Code Review',
    'Design Session',
    'Focus Time',
    'Planning',
    'Research',
    'Write Docs',
    'Test & QA'
  ];

  function getRandomTaskName(): string {
    const index = Math.floor(Math.random() * TASK_NAME_CHOICES.length);
    return TASK_NAME_CHOICES[index];
  }

  let taskNames: Record<string, string> = {};

  // Initialize names for the initial agenda items
  for (const item of agenda_items) {
    taskNames[item.uuid] = getRandomTaskName();
  }

  // Handle changes from the TimeWheel component
  function handleAgendaItemsChanged(event: CustomEvent) {
    const updatedItems: AgendaItem[] = event.detail.agendaItems;
    const updatedUuidSet = new Set(updatedItems.map((item) => item.uuid));

    // Remove names for items that no longer exist
    for (const uuid of Object.keys(taskNames)) {
      if (!updatedUuidSet.has(uuid)) {
        delete taskNames[uuid];
      }
    }

    // Assign names for any new items missing a name
    for (const item of updatedItems) {
      if (!taskNames[item.uuid]) {
        taskNames[item.uuid] = getRandomTaskName();
      }
    }

    agenda_items = updatedItems;
    console.log('Agenda items updated from wheel:', agenda_items);
  }

  // Example: Add a new agenda item from the main app
  function addNewItem() {
    const DEFAULT_DURATION = 2;
    const lastEnd = agenda_items.length > 0
      ? Math.max(...agenda_items.map((item) => item.e_time))
      : 0;
    const startTime = lastEnd;
    const endTime = startTime + DEFAULT_DURATION;

    const newItem: AgendaItem = { s_time: startTime, e_time: endTime, color: 'red', uuid: uuidv4() };
    agenda_items = [
      ...agenda_items,
      newItem
    ];
    taskNames[newItem.uuid] = getRandomTaskName();
  }

  // Example: Remove the first agenda item
  function removeFirstItem() {
    if (agenda_items.length > 0) {
      const [removed, ...rest] = agenda_items;
      agenda_items = rest;
      if (removed) {
        delete taskNames[removed.uuid];
      }
    }
  }

  
</script>

<div class="container">
  <div class="left">
    <h3>Agenda Controls</h3>
    <p>Current items: {agenda_items.length}</p>
    <button on:click={addNewItem}>Add Task After Last</button>
    <button on:click={removeFirstItem}>Remove First Item</button>
    
    <h4>Current Agenda Items:</h4>
    <ul>
      {#each agenda_items as item, index}
        <li>
          <span class="color-swatch" style="background-color: {item.color};"></span>
          {taskNames[item.uuid] || ('Task ' + (index + 1))}: {item.s_time}-{item.e_time}
        </li>
      {/each}
    </ul>
  </div>
  <div class="right">
    <TimeWheel 
      start={0} 
      offset={0} 
      agendaItems={agenda_items}
      on:agendaItemsChanged={handleAgendaItemsChanged}
    />
  </div>
</div>

<style>
  .color-swatch {
    display: inline-block;
    width: 0.8rem;
    height: 0.8rem;
    border-radius: 2px;
    margin-right: 0.5rem;
    border: 1px solid rgba(0, 0, 0, 0.1);
    vertical-align: middle;
  }
</style>