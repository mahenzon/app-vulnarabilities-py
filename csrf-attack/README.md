# CSRF Attack (Cross-Site Request Forgery)

## Problem

**CSRF** (Cross-Site Request Forgery) is a type of attack on website visitors that exploits weaknesses in the HTTP protocol.

### How the Attack Works

When a victim visits a website created by an attacker, a request is secretly sent on their behalf to another server (for example, a payment system server), performing a malicious operation (such as transferring money to the attacker's account).

### Conditions for a Successful Attack

For a CSRF attack to be successful:
- The victim must be authenticated on the server to which the request is sent
- The request must not require user confirmation that cannot be forged
- The attacking script can form and send a request without the user's knowledge

### The Danger

CSRF attacks can affect:
- Public web applications
- Internal services (not directly accessible from outside)
- Administration panels
- API endpoints that modify data state

Therefore, CSRF protection is critically important for any applications working with user data.

## Solution

### Main Protection Principle

All requests that modify data state (create, update, delete) must be signed with a special **CSRF token**.

### Token Mechanism

1. **Generation**: The server generates a unique unpredictable token for each session or request
2. **Embedding**: The token is embedded in HTML forms or passed in headers
3. **Validation**: When receiving a request, the server checks the presence and correctness of the token
4. **Rejection**: Requests without a valid token are rejected

### HTML Implementation Example

```html
<form method="post" action="/transfer">
    <input type="hidden" name="csrf_token" value="UNIQUE_TOKEN"/>
    <input type="text" name="recipient" placeholder="Recipient"/>
    <input type="number" name="amount" placeholder="Amount"/>
    <button type="submit">Send</button>
</form>
```

### Server-Side Validation Example

When processing a POST request, the server should:

```python
# Pseudocode
def process_transfer(request):
    # 1. Extract token from request
    token_from_request = request.form.get('csrf_token')

    # 2. Get expected token from session
    expected_token = request.session.get('csrf_token')

    # 3. Compare tokens
    if not token_from_request or token_from_request != expected_token:
        raise SecurityError("Invalid CSRF token")

    # 4. Execute operation only if token is valid
    perform_transfer(request.form.get('recipient'), request.form.get('amount'))
```

### Additional Protection Measures

1. **SameSite cookies**: Setting the `SameSite=Strict` or `SameSite=Lax` attribute for cookies prevents them from being sent in cross-site requests

2. **Origin/Referer header verification**: Verify that the request came from the same domain

3. **Confirmation requirement**: For critical operations (e.g., password change, large transfers), require additional confirmation (password, 2FA)

4. **Token lifetime limitation**: Tokens should have an expiration time
