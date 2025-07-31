<!-- App.svelte -->
<script lang="ts">
  import TimeWheel from './components/TimeWheel.svelte';

  type AgendaItem = {
    s_time: number,
    e_time: number,
    color: string,
  }

  let agenda_items: AgendaItem[] = [
    { s_time: 4, e_time: 6, color: 'blue' },
    { s_time: 8, e_time: 10, color: 'green' }
  ];

  // Handle changes from the TimeWheel component
  function handleAgendaItemsChanged(event: CustomEvent) {
    agenda_items = event.detail.agendaItems;
    console.log('Agenda items updated from wheel:', agenda_items);
  }

  // Example: Add a new agenda item from the main app
  function addNewItem() {
    agenda_items = [
      ...agenda_items,
      { s_time: 12, e_time: 14, color: 'red' }
    ];
  }

  // Example: Remove the first agenda item
  function removeFirstItem() {
    if (agenda_items.length > 0) {
      agenda_items = agenda_items.slice(1);
    }
  }

  // Example: Modify the first item's color
  function changeFirstItemColor() {
    if (agenda_items.length > 0) {
      agenda_items = agenda_items.map((item, index) => 
        index === 0 ? { ...item, color: 'purple' } : item
      );
    }
  }
</script>

<div class="container">
  <div class="left">
    <h3>Agenda Controls</h3>
    <p>Current items: {agenda_items.length}</p>
    <button on:click={addNewItem}>Add Red Item (12-14)</button>
    <button on:click={removeFirstItem}>Remove First Item</button>
    <button on:click={changeFirstItemColor}>Change First Item to Purple</button>
    
    <h4>Current Agenda Items:</h4>
    <ul>
      {#each agenda_items as item, index}
        <li>
          Item {index + 1}: {item.s_time}-{item.e_time} ({item.color})
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