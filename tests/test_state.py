from manta import state
from datetime import datetime

def test_add_review(temp_state_file):
    local = "/tmp/test.md"
    remote = "/storage/test.pdf"
    
    state.add_review(local, remote)
    
    pending = state.get_pending_reviews()
    assert local in pending
    assert pending[local]['device_path'] == remote
    assert pending[local]['status'] == 'pending'

def test_mark_completed(temp_state_file):
    local = "/tmp/test.md"
    state.add_review(local, "/storage/test.pdf")
    
    state.mark_completed(local)
    
    pending = state.get_pending_reviews()
    assert local not in pending
    
    # Check underlying file content
    data = state.load_state()
    assert data['reviews'][local]['status'] == 'completed'
    assert 'completed_at' in data['reviews'][local]

def test_empty_state(temp_state_file):
    assert state.get_pending_reviews() == {}
