import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SpecialNoteStats {
  note_text: string;
  usage_count: number;
  last_used: string;
}

/**
 * Get the top N most used special notes
 * @param limit - Number of top notes to retrieve (default: 3)
 * @returns Array of special note statistics
 */
export async function getTopSpecialNotes(limit: number = 3): Promise<SpecialNoteStats[]> {
  try {
    const response = await axios.get(`${API_URL}/api/special-notes/top`, {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching top special notes:', error);
    return [];
  }
}

/**
 * Record usage of a special note
 * @param noteText - The special note text to record
 */
export async function recordSpecialNoteUsage(noteText: string): Promise<void> {
  try {
    await axios.post(`${API_URL}/api/special-notes/record`, {
      note_text: noteText
    });
  } catch (error) {
    console.error('Error recording special note usage:', error);
    // Don't throw - this is a non-critical operation
  }
}

export default {
  getTopSpecialNotes,
  recordSpecialNoteUsage
};
