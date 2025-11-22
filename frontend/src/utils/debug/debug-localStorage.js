// Debug script to inspect localStorage tasks
// Run this in browser console to see what tasks are stored

console.log('=== DEBUGGING LOCALSTORAGE TASKS ===');

// Get all task keys
const taskKeys = Object.keys(localStorage).filter(key => key.startsWith('task_'));
console.log(`Found ${taskKeys.length} task keys:`, taskKeys);

// Analyze each task
const allTasks = [];
const guestTasks = [];
const otherTasks = [];

taskKeys.forEach(key => {
  try {
    const taskData = localStorage.getItem(key);
    if (taskData) {
      const task = JSON.parse(taskData);
      allTasks.push(task);
      
      if (task.user_id === 'guest') {
        guestTasks.push(task);
      } else {
        otherTasks.push(task);
      }
      
      console.log(`${key}:`, {
        id: task.id,
        title: task.title,
        user_id: task.user_id,
        status: task.status,
        due_date: task.due_date
      });
    }
  } catch (error) {
    console.error(`Error parsing ${key}:`, error);
  }
});

console.log('\n=== SUMMARY ===');
console.log(`Total tasks in localStorage: ${allTasks.length}`);
console.log(`Guest tasks (user_id === 'guest'): ${guestTasks.length}`);
console.log(`Other tasks: ${otherTasks.length}`);

// Count by status for guest tasks
const guestPending = guestTasks.filter(t => t.status === 'pending').length;
const guestCompleted = guestTasks.filter(t => t.status === 'completed').length;

console.log(`\nGuest task breakdown:`);
console.log(`- Pending: ${guestPending}`);
console.log(`- Completed: ${guestCompleted}`);

// Show other tasks if any
if (otherTasks.length > 0) {
  console.log('\n=== NON-GUEST TASKS ===');
  otherTasks.forEach(task => {
    console.log(`- ${task.title} (user_id: ${task.user_id}, status: ${task.status})`);
  });
}
