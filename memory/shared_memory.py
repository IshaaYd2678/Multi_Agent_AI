# memory/shared_memory.py
import json
import os
import tempfile
from datetime import datetime
from collections import defaultdict, Counter

class EnhancedMemoryStore:
    def __init__(self, storage_file="memory_store.json"):
        self.storage_file = storage_file
        self.memory_store = {}
        self.analytics = defaultdict(list)
        self.load_from_disk()
    
    def save_context(self, doc_id, data):
        """Save context with timestamp and metadata"""
        enhanced_data = {
            **data,
            "saved_at": datetime.now().isoformat(),
            "doc_id": doc_id
        }
        
        self.memory_store[doc_id] = enhanced_data
        
        # Update analytics
        self.update_analytics(doc_id, data)
        
        # Auto-save to disk
        self.save_to_disk()
        
        return enhanced_data
    
    def get_context(self, doc_id):
        """Retrieve context by document ID"""
        return self.memory_store.get(doc_id, {})
    
    def search_contexts(self, query, limit=10):
        """Search contexts by content"""
        results = []
        query_lower = query.lower()
        
        for doc_id, context in self.memory_store.items():
            score = 0
            
            # Search in various fields
            searchable_fields = ['format', 'intent', 'sender', 'subject', 'document_type']
            for field in searchable_fields:
                if field in context and query_lower in str(context[field]).lower():
                    score += 1
            
            # Search in extracted info
            if 'extracted_info' in context:
                for value in context['extracted_info'].values():
                    if query_lower in str(value).lower():
                        score += 0.5
            
            if score > 0:
                results.append((doc_id, context, score))
        
        # Sort by relevance score
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]
    
    def get_analytics(self):
        """Get processing analytics"""
        total_docs = len(self.memory_store)
        
        # Count by format
        formats = Counter()
        intents = Counter()
        urgency_levels = Counter()
        
        for context in self.memory_store.values():
            if 'format' in context:
                formats[context['format']] += 1
            if 'intent' in context:
                intents[context['intent']] += 1
            if 'urgency' in context:
                urgency_levels[context['urgency']] += 1
        
        return {
            "total_documents": total_docs,
            "formats": dict(formats),
            "intents": dict(intents),
            "urgency_levels": dict(urgency_levels),
            "recent_activity": self.get_recent_activity()
        }
    
    def get_recent_activity(self, days=7):
        """Get recent processing activity"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_docs = []
        
        for doc_id, context in self.memory_store.items():
            if 'saved_at' in context:
                try:
                    saved_date = datetime.fromisoformat(context['saved_at'])
                    if saved_date > cutoff_date:
                        recent_docs.append({
                            "doc_id": doc_id,
                            "format": context.get('format', 'Unknown'),
                            "intent": context.get('intent', 'Unknown'),
                            "saved_at": context['saved_at']
                        })
                except:
                    pass
        
        return sorted(recent_docs, key=lambda x: x['saved_at'], reverse=True)
    
    def update_analytics(self, doc_id, data):
        """Update analytics data"""
        timestamp = datetime.now().isoformat()
        
        self.analytics['processing_history'].append({
            "doc_id": doc_id,
            "timestamp": timestamp,
            "format": data.get('format'),
            "intent": data.get('intent')
        })
        
        # Keep only last 1000 entries
        if len(self.analytics['processing_history']) > 1000:
            self.analytics['processing_history'] = self.analytics['processing_history'][-1000:]
    
    def save_to_disk(self):
        """Save memory store to disk"""
        try:
            data_to_save = {
                "memory_store": self.memory_store,
                "analytics": dict(self.analytics),
                "last_saved": datetime.now().isoformat()
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            fallback_file = os.path.join(tempfile.gettempdir(), "multi_agent_ai_memory_store.json")
            if os.path.abspath(self.storage_file) == os.path.abspath(fallback_file):
                print(f"Error saving to disk: {e}")
                return

            try:
                self.storage_file = fallback_file
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            except Exception as fallback_error:
                print(f"Error saving to disk: {fallback_error}")
    
    def load_from_disk(self):
        """Load memory store from disk"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory_store = data.get('memory_store', {})
                    self.analytics = defaultdict(list, data.get('analytics', {}))
        except Exception as e:
            print(f"Error loading from disk: {e}")
            self.memory_store = {}
            self.analytics = defaultdict(list)
    
    def clear_old_entries(self, days=30):
        """Clear entries older than specified days"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        to_remove = []
        
        for doc_id, context in self.memory_store.items():
            if 'saved_at' in context:
                try:
                    saved_date = datetime.fromisoformat(context['saved_at'])
                    if saved_date < cutoff_date:
                        to_remove.append(doc_id)
                except:
                    pass
        
        for doc_id in to_remove:
            del self.memory_store[doc_id]
        
        self.save_to_disk()
        return len(to_remove)

# Global instance
memory_store_instance = EnhancedMemoryStore()

# Backward compatibility functions
def save_context(doc_id, data):
    return memory_store_instance.save_context(doc_id, data)

def get_context(doc_id):
    return memory_store_instance.get_context(doc_id)

def search_contexts(query, limit=10):
    return memory_store_instance.search_contexts(query, limit)

def get_analytics():
    return memory_store_instance.get_analytics()
