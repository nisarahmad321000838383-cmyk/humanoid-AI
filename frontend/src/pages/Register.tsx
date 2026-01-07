import { useState, FormEvent, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { UserPlus, Sparkles, Check, X } from 'lucide-react';
import { apiService } from '@/services/api';
import './Auth.css';

interface PasswordValidation {
  minLength: boolean;
  hasUpperCase: boolean;
  hasNumber: boolean;
  hasSpecialChar: boolean;
}

const Register = () => {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError, isAuthenticated } = useAuthStore();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
  });
  const [passwordValidation, setPasswordValidation] = useState<PasswordValidation>({
    minLength: false,
    hasUpperCase: false,
    hasNumber: false,
    hasSpecialChar: false,
  });
  const [showValidation, setShowValidation] = useState(false);
  const [usernameError, setUsernameError] = useState<string>('');
  const [emailError, setEmailError] = useState<string>('');
  const [checkingUsername, setCheckingUsername] = useState(false);
  const [checkingEmail, setCheckingEmail] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/chat');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    clearError();
  }, [clearError]);

  useEffect(() => {
    // Validate password in real-time
    const password = formData.password;
    setPasswordValidation({
      minLength: password.length >= 8,
      hasUpperCase: /[A-Z]/.test(password),
      hasNumber: /[0-9]/.test(password),
      hasSpecialChar: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    });
  }, [formData.password]);

  // Check username availability in real-time
  useEffect(() => {
    const checkUsername = async () => {
      if (!formData.username || formData.username.length < 3) {
        setUsernameError('');
        return;
      }

      setCheckingUsername(true);
      try {
        const result = await apiService.checkAvailability({ username: formData.username });
        if (result.username_available === false) {
          setUsernameError(result.username_message || 'This username is already taken. Please try another one.');
        } else {
          setUsernameError('');
        }
      } catch (error) {
        console.error('Error checking username:', error);
      } finally {
        setCheckingUsername(false);
      }
    };

    const timeoutId = setTimeout(checkUsername, 500); // Debounce for 500ms
    return () => clearTimeout(timeoutId);
  }, [formData.username]);

  // Check email availability in real-time
  useEffect(() => {
    const checkEmail = async () => {
      if (!formData.email || !formData.email.includes('@')) {
        setEmailError('');
        return;
      }

      setCheckingEmail(true);
      try {
        const result = await apiService.checkAvailability({ email: formData.email });
        if (result.email_available === false) {
          setEmailError(result.email_message || 'This email is already taken. Please try another one.');
        } else {
          setEmailError('');
        }
      } catch (error) {
        console.error('Error checking email:', error);
      } finally {
        setCheckingEmail(false);
      }
    };

    const timeoutId = setTimeout(checkEmail, 500); // Debounce for 500ms
    return () => clearTimeout(timeoutId);
  }, [formData.email]);

  const isPasswordValid = 
    passwordValidation.minLength &&
    passwordValidation.hasUpperCase &&
    passwordValidation.hasNumber &&
    passwordValidation.hasSpecialChar;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (formData.password !== formData.password2) {
      return;
    }

    if (!isPasswordValid) {
      return;
    }

    try {
      await register(formData);
      navigate('/chat');
    } catch (error) {
      // Error is handled by store
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-content">
        <div className="auth-header">
          <div className="logo">
            <Sparkles size={32} />
            <h1>Humanoid AI</h1>
          </div>
          <p className="slogan">No Hallucination</p>
        </div>

        <div className="auth-card">
          <h2>Create an account</h2>
          <p className="auth-subtitle">Start chatting with Humanoid AI</p>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">First Name</label>
                <input
                  id="first_name"
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  placeholder="First name"
                  autoComplete="given-name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="last_name">Last Name</label>
                <input
                  id="last_name"
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  placeholder="Last name"
                  autoComplete="family-name"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="Choose a username"
                required
                autoComplete="username"
                className={usernameError ? 'input-error' : ''}
              />
              {checkingUsername && <small className="checking-text">Checking availability...</small>}
              {usernameError && <small className="error-text">{usernameError}</small>}
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="your.email@example.com"
                required
                autoComplete="email"
                className={emailError ? 'input-error' : ''}
              />
              {checkingEmail && <small className="checking-text">Checking availability...</small>}
              {emailError && <small className="error-text">{emailError}</small>}
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                onFocus={() => setShowValidation(true)}
                placeholder="Create a password"
                required
                autoComplete="new-password"
              />
              {showValidation && formData.password && (
                <div className="password-validation">
                  <div className={`validation-item ${passwordValidation.minLength ? 'valid' : 'invalid'}`}>
                    {passwordValidation.minLength ? <Check size={16} /> : <X size={16} />}
                    <span>At least 8 characters</span>
                  </div>
                  <div className={`validation-item ${passwordValidation.hasUpperCase ? 'valid' : 'invalid'}`}>
                    {passwordValidation.hasUpperCase ? <Check size={16} /> : <X size={16} />}
                    <span>One uppercase letter</span>
                  </div>
                  <div className={`validation-item ${passwordValidation.hasNumber ? 'valid' : 'invalid'}`}>
                    {passwordValidation.hasNumber ? <Check size={16} /> : <X size={16} />}
                    <span>One number</span>
                  </div>
                  <div className={`validation-item ${passwordValidation.hasSpecialChar ? 'valid' : 'invalid'}`}>
                    {passwordValidation.hasSpecialChar ? <Check size={16} /> : <X size={16} />}
                    <span>One special character (!@#$%^&*...)</span>
                  </div>
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="password2">Confirm Password</label>
              <input
                id="password2"
                type="password"
                value={formData.password2}
                onChange={(e) => setFormData({ ...formData, password2: e.target.value })}
                placeholder="Confirm your password"
                required
                autoComplete="new-password"
              />
            </div>

            {formData.password !== formData.password2 && formData.password2 && (
              <div className="error-message">
                Passwords do not match
              </div>
            )}

            <button
              type="submit"
              className="auth-button"
              disabled={isLoading || formData.password !== formData.password2 || !isPasswordValid || !!usernameError || !!emailError || checkingUsername || checkingEmail}
            >
              {isLoading ? (
                'Creating account...'
              ) : (
                <>
                  <UserPlus size={18} />
                  Create Account
                </>
              )}
            </button>
          </form>

          <div className="auth-footer">
            <p>
              Already have an account?{' '}
              <Link to="/login" className="auth-link">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
