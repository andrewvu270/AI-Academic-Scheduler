// Test script to verify logout cleanup functionality
// Run this in browser console BEFORE logout to see what data exists
// Then run after logout to verify it's all cleared

console.log('=== TESTING LOGOUT CLEANUP ===');

// Function to check localStorage data
function checkLocalStorageData() {
  const allKeys = Object.keys(localStorage);
  const guestKeys = allKeys.filter(key => 
    key.startsWith('task_') || 
    key.startsWith('course_') || 
    key === 'guest_session_id' ||
    key.startsWith('uploaded_files') ||
    key.startsWith('guest_')
  );
  
  console.log('All localStorage keys:', allKeys.length);
  console.log('Guest-related keys:', guestKeys.length);
  
  if (guestKeys.length > 0) {
    console.log('Guest keys found:', guestKeys);
    
    // Count tasks
    const taskKeys = guestKeys.filter(k => k.startsWith('task_'));
    console.log(`Tasks: ${taskKeys.length}`);
    
    // Count courses  
    const courseKeys = guestKeys.filter(k => k.startsWith('course_'));
    console.log(`Courses: ${courseKeys.length}`);
  } else {
    console.log('✅ No guest data found - localStorage is clean!');
  }
  
  return guestKeys.length;
}

// Check current state
const guestDataCount = checkLocalStorageData();

if (guestDataCount > 0) {
  console.log('\n📝 Instructions:');
  console.log('1. Log out using the navigation menu');
  console.log('2. Run this script again to verify cleanup');
  console.log('3. You should see "No guest data found" message');
} else {
  console.log('\n✅ Logout cleanup test PASSED - no guest data present');
}
