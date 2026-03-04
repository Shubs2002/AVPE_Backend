"""
Test script to verify error detection for code 13 (internal server error)
"""

def test_error_detection():
    """Test that code 13 errors are detected as retryable"""
    
    # Simulate the error message format
    error_messages = [
        # Code 13 - Internal server error
        "Video generation failed: {'code': 13, 'message': 'Video generation failed due to an internal server issue. Please try again in a few minutes. If the problem persists, please contact Gemini API support.'}",
        
        # Code 14 - Overloaded
        "Video generation failed: {'code': 14, 'message': 'Service is currently overloaded'}",
        
        # RAI filter error
        "Failed to parse: generated_videos=None rai_media_filtered_count=1 rai_media_filtered_reasons=['Sorry, we can't create videos from input images containing celebrity or their likenesses. Please remove the reference and try again.']",
        
        # Generic internal server error
        "Video generation failed due to an internal server issue",
        
        # Rate limit
        "Rate limit exceeded",
        
        # Quota exceeded
        "Quota exceeded",
    ]
    
    # Test detection logic from content_to_video_service.py
    def is_temporary_error(error_str):
        error_str_lower = str(error_str).lower()
        return (
            "overloaded" in error_str_lower or 
            "rate" in error_str_lower or 
            "quota" in error_str_lower or
            "internal server" in error_str_lower or
            "'code': 13" in str(error_str) or
            "server issue" in error_str_lower or
            "try again" in error_str_lower
        )
    
    # Test detection logic from genai_service.py
    def is_transient_service_error(exc_or_obj):
        try:
            text = str(exc_or_obj).lower()
            transient_indicators = [
                "unavailable",
                "503",
                "service is currently unavailable",
                "overloaded",
                "'code': 14",
                "currently overloaded",
                "'code': 13",
                "internal server issue",
                "internal server error",
                "please try again",
                "please try again later",
                "rate",  # Rate limit errors
                "quota",  # Quota exceeded errors
                "rai_media_filtered",
                "rai filter",
                "content filter",
                "celebrity or their likenesses",
                "generated_videos=none"
            ]
            return any(indicator in text for indicator in transient_indicators)
        except Exception:
            pass
        return False
    
    print("="*60)
    print("Testing Error Detection Logic")
    print("="*60)
    
    for i, error_msg in enumerate(error_messages, 1):
        print(f"\n{i}. Testing error:")
        print(f"   {error_msg[:100]}...")
        
        temp_error = is_temporary_error(error_msg)
        transient_error = is_transient_service_error(error_msg)
        
        print(f"   ✅ content_to_video_service: {'RETRYABLE' if temp_error else 'NOT RETRYABLE'}")
        print(f"   ✅ genai_service: {'RETRYABLE' if transient_error else 'NOT RETRYABLE'}")
        
        if not (temp_error and transient_error):
            print(f"   ⚠️  WARNING: Error not detected as retryable!")
    
    print("\n" + "="*60)
    print("✅ Error Detection Test Complete")
    print("="*60)
    
    # Test the specific error from the user
    print("\n" + "="*60)
    print("Testing User's Specific Error")
    print("="*60)
    
    user_error = "Video generation failed: {'code': 13, 'message': 'Video generation failed due to an internal server issue. Please try again in a few minutes. If the problem persists, please contact Gemini API support.'}"
    
    print(f"\nError: {user_error}")
    print(f"\nDetection Results:")
    print(f"  content_to_video_service: {'✅ RETRYABLE' if is_temporary_error(user_error) else '❌ NOT RETRYABLE'}")
    print(f"  genai_service: {'✅ RETRYABLE' if is_transient_service_error(user_error) else '❌ NOT RETRYABLE'}")
    
    # Check specific patterns
    print(f"\nPattern Checks:")
    code_13_pattern = "'code': 13"
    print(f"  Contains '{code_13_pattern}': {code_13_pattern in user_error}")
    print(f"  Contains 'internal server' (lowercase): {'internal server' in user_error.lower()}")
    print(f"  Contains 'please try again' (lowercase): {'please try again' in user_error.lower()}")


if __name__ == "__main__":
    test_error_detection()
