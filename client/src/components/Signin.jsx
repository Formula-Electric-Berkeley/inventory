import { getAuth, GoogleAuthProvider } from 'firebase/auth';
import { signInWithPopup } from '../firebase';

const SignIn = () => {
    const signInWithGoogle = async () => {
        const auth = getAuth();
        const provider = new GoogleAuthProvider();

        try {
            const result = await signInWithPopup(auth, provider);
            const user = result.user;
            const idToken = await user.getIdToken();
            return { name: user.displayName, token: idToken };
        } catch (error) {
            console.error("Error during sign-in:", error);
            return null;
        }
    };

    const handleGoogleSignIn = async () => {
        const userData = await signInWithGoogle();
        if (userData) {
            const response = await fetch(`${window.env.REACT_APP_API_URL}/api/user/google_auth`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(userData),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("token", data.token)
                localStorage.setItem("name", data.name)
                window.location.href = `/`;
            } else {
                console.error("Authentication failed:", await response.json());
            }
        }
    };

    return (
        <div>
            {localStorage.getItem("token") ?
                localStorage.getItem("name") :
                <button onClick={handleGoogleSignIn}>
                    Sign in with Google
                </button>
            }
        </div>
    );
};

export default SignIn;
