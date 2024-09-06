import { getAuth, GoogleAuthProvider } from 'firebase/auth';
import { signInWithPopup } from '../firebase';

const SignIn = () => {
    const signInWithGoogle = async () => {
        const auth = getAuth();
        const provider = new GoogleAuthProvider();

        try {
            const result = await signInWithPopup(auth, provider);
            const user = result.user;
            const idToken = await user.getIdToken();  // Obtain the Firebase ID token
            return idToken;
        } catch (error) {
            console.error("Error during sign-in:", error);
            return null;
        }
    };

    const handleGoogleSignIn = async () => {
        const idToken = await signInWithGoogle();
        if (idToken) {
            const response = await fetch(`${window.env.REACT_APP_API_URL}/api/user/google_auth`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",  // Set the content type to JSON
                },
                body: JSON.stringify({ token: idToken }),  // Send the idToken in the body
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Authentication successful:", data);
                // You can handle further actions, like storing user data or redirecting
            } else {
                console.error("Authentication failed:", await response.json());
            }
        }
    };

    return (
        <div>
            <button onClick={handleGoogleSignIn}>Sign in with Google</button>
        </div>
    );
};

export default SignIn;
