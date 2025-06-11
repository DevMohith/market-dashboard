import { v4 as uuidv4 } from 'uuid'; // For generating unique IDs

const USER_ID_KEY = 'market_dashboard_pseudo_user_id';

export const getPseudoUserId = () => {
  let userId = localStorage.getItem(USER_ID_KEY);
  if (!userId) {
    userId = uuidv4(); // Generate a new UUID if not found
    localStorage.setItem(USER_ID_KEY, userId);
    console.log(`Generated new pseudo user ID: ${userId}`);
  } else {
    console.log(`Using existing pseudo user ID: ${userId}`);
  }
  return userId;
};
