<!-- TimeWheel.svelte -->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';

  export let start: number = 0; // Starting hour
  export let offset: number = 0; // Offset in radians
  export let agendaItems: AgendaItem[] = [];

  const dispatch = createEventDispatcher();

  type AgendaItem = {
    s_time: number,
    e_time: number,
    color: string,
  }

  let canvas: HTMLCanvasElement;

  function peg_to_rad(offset: number) {
    return (i: number) => ((i / (12.0 * 4.0)) * (2 * Math.PI)) - Math.PI / 2 + offset
  }

  function rad_to_peg(offset: number) {
    return (rad: number) => (rad - offset + Math.PI / 2) / (2 * Math.PI) * (12.0 * 4.0)
  }

  function circle_coords(center: [number, number], radius: number, theta: number): [number, number] {
    let [centerX, centerY] = center
    return [Math.cos(theta) * radius + centerX, Math.sin(theta) * radius + centerY]
  }

  function drawAgendaItems(agendaItems: AgendaItem[], start: number, offset: number, size: number, context: CanvasRenderingContext2D) {
    const radius = size / 2.4
    const width = radius * 2.4;
    const height = radius * 2.4;
    console.log(agendaItems)
    for (let agendaItem of agendaItems) {
      let { s_time, e_time, color } = agendaItem
      let [s_theta, e_theta] = [s_time, e_time].map(peg_to_rad(offset))
      context.fillStyle = color;
      context.beginPath();
      context.moveTo(width / 2, height / 2);
      context.lineTo(...circle_coords([width / 2, height / 2], radius, s_theta))
      context.arc(width / 2, height / 2, radius, s_theta, e_theta, false);
      context.fill()
    }
    return context.canvas
  }

  function drawWheelBase(start: number, offset: number, size: number, context: CanvasRenderingContext2D) {
    const radius = size / 2.4
    const width = radius * 2.4;
    const height = radius * 2.4;
    context.beginPath();
    context.arc(width / 2, height / 2, radius, 0, 2 * Math.PI, false);
    context.stroke()

    let fontSize = Math.round(radius * 0.05);
    let font = fontSize + "px Courier";

    for (let i = 0; i < 12 * 4; i++) {
      let n_theta = peg_to_rad(offset)(i)
      let [sx, sy] = circle_coords([width / 2, height / 2], radius * (1.0), n_theta)

      let scale = 0.05
      scale *= (i % 4 == 0 ? 1.0 : (2.0 / 3.0))
      scale *= (i % 2 == 0 ? 1.0 : 0.5)

      let [ex, ey] = circle_coords([width / 2, height / 2], radius * (1.0 + scale), n_theta)

      context.beginPath();
      context.moveTo(sx, sy);
      context.lineTo(ex, ey);
      context.stroke();

      if (i % 4 == 0) {
        context.fillStyle = "black"
        context.font = font;
        context.textAlign = "center";
        context.textBaseline = "middle";

        let [tx, ty] = circle_coords([width / 2, height / 2], radius * (1.1), n_theta)
        let time = (i / 4 + start) % 12
        let text = time == 0 ? 12 : time
        context.fillText('' + text, tx, ty);
      }
    }
    return context.canvas
  }

  function redraw() {
    if (!canvas) return; // Early return if canvas is not initialized
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const size = Math.min(canvas.offsetWidth, canvas.offsetHeight);
    ctx.clearRect(0, 0, size, size);
    drawWheelBase(start, offset, size, ctx);
    drawAgendaItems(agendaItems, start, offset, size, ctx);
  }

  onMount(() => {
    const resizeCanvas = () => {
      // Get the display size of the canvas
      const dpr = window.devicePixelRatio || 1; // Handle high-DPI displays

      canvas.width = canvas.offsetWidth * dpr;
      canvas.height = canvas.offsetHeight * dpr;

      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Scale context to account for DPR
        ctx.scale(dpr, dpr);
        
        // Draw the clock wheel
        const size = Math.min(canvas.offsetWidth, canvas.offsetHeight);
        drawWheelBase(start, offset, size, ctx);
        drawAgendaItems(agendaItems, start, offset, size, ctx);
      }
    };

    // Initial resize
    resizeCanvas();

    canvas.addEventListener('contextmenu', function (event) {
      event.preventDefault();
    });

    canvas.addEventListener('mousedown', function (event) {
      const context = canvas.getContext('2d');
      if (!context) return;
      const rect = context.canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      const size = Math.min(canvas.offsetWidth, canvas.offsetHeight);
      //for some reason canvas width and height are off
      const rel_x = x - size / 2
      const rel_y = y - size / 2

      const theta = Math.atan2(rel_y, rel_x)
      console.log(`Mouse position: (${x}, ${y}), Relative position: (${rel_x}, ${rel_y}), Theta: ${theta}`);
      const peg = rad_to_peg(offset)(theta)

      const agenda_in = agendaItems.find(({ s_time, e_time }) => (s_time <= peg) && (peg <= e_time))
      var add = 0;
      if (event.button === 0) add = 1;
      if (event.button === 2) add = -1;
      
      // Create a new array to avoid mutating the original
      const updatedAgendaItems = [...agendaItems];
      
      if (agenda_in) {
        const index = updatedAgendaItems.indexOf(agenda_in);
        if ((agenda_in.e_time - agenda_in.s_time > 1) || (add == 1)) {
          updatedAgendaItems[index] = { ...agenda_in, e_time: agenda_in.e_time + add };
        }
      }
      
      updatedAgendaItems.forEach((item, index) => {
        if (item.s_time > peg && !(agenda_in && event.button === 2)) {
          updatedAgendaItems[index] = {
            ...item,
            s_time: item.s_time + add,
            e_time: item.e_time + add
          };
        }
      });
      
      // Dispatch the updated agenda items to the parent
      dispatch('agendaItemsChanged', { agendaItems: updatedAgendaItems });
    })

    // Handle window resize
    window.addEventListener('resize', resizeCanvas);
    return () => window.removeEventListener('resize', resizeCanvas);
  });

  // Watch for changes in agendaItems and redraw
  $: if (agendaItems && canvas) {
    redraw();
  }
</script>

<canvas bind:this={canvas}></canvas> 