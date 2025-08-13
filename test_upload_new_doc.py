#!/usr/bin/env python3
"""
Upload a new test document and test document filtering.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def upload_and_test():
    """Upload a new document and test filtering."""
    
    print("📤 Uploading New Test Document")
    print("=" * 50)
    
    # Upload the new test document
    with open("test_new_document.txt", "rb") as f:
        files = {"file": ("test_new_document.txt", f, "text/plain")}
        
        print("Uploading test_new_document.txt...")
        response = requests.post(f"{API_BASE_URL}/documents/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            document_id = result.get("document_id")
            print(f"✅ Upload successful! Document ID: {document_id}")
            
            # Wait for processing to complete
            print("⏳ Waiting for processing to complete...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                
                progress_response = requests.get(f"{API_BASE_URL}/documents/upload/{document_id}/progress")
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    if progress.get("status") == "completed":
                        print("✅ Processing completed!")
                        break
                    elif progress.get("status") == "failed":
                        print(f"❌ Processing failed: {progress.get('error_message', 'Unknown error')}")
                        return
                    else:
                        print(f"⏳ Processing... {progress.get('progress', 0)}%")
                else:
                    print("⚠️ Could not check progress")
            
            # Test query with document filtering
            print(f"\n🧪 Testing Document Filtering")
            print("=" * 30)
            
            # Test query that should match the new document
            query_data = {
                "query": "What is document filtering?",
                "document_ids": [document_id],
                "top_k": 5,
                "score_threshold": 0.3
            }
            
            print(f"Query: 'What is document filtering?' (Filtered to document: {document_id})")
            
            response = requests.post(f"{API_BASE_URL}/query", json=query_data)
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', 'No answer')
                sources = result.get('sources', [])
                
                print(f"✅ Query successful!")
                print(f"Answer: {answer}")
                print(f"Sources found: {len(sources)}")
                
                for i, source in enumerate(sources):
                    print(f"  Source {i+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
                    print(f"    Preview: {source.get('content_preview', 'No preview')[:100]}...")
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
            
            # Test query without filtering (should also work)
            print(f"\n🧪 Testing Query Without Filtering")
            print("=" * 30)
            
            query_data = {
                "query": "What is document filtering?",
                "top_k": 5,
                "score_threshold": 0.3
            }
            
            print(f"Query: 'What is document filtering?' (No filtering)")
            
            response = requests.post(f"{API_BASE_URL}/query", json=query_data)
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', 'No answer')
                sources = result.get('sources', [])
                
                print(f"✅ Query successful!")
                print(f"Answer: {answer}")
                print(f"Sources found: {len(sources)}")
                
                for i, source in enumerate(sources):
                    print(f"  Source {i+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
                    print(f"    Preview: {source.get('content_preview', 'No preview')[:100]}...")
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
    
    print("\n" + "=" * 50)
    print("🏁 Upload and test completed!")

if __name__ == "__main__":
    upload_and_test()
