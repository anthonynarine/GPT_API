import { useState, useCallback } from "react";
import axios from "axios";


const useGptRequest = () => {
    // State variables to manage the GPT response, loading state, and errors
    const [gptResponse, setGptResponse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [chatHistory, setChatHistory] = useState([]); // State to manage chat history

    const base_url = "http://localhost:8000/api/gpt/"
    const production_url = 'https://gait-gpt.herokuapp.com/api/gpt/'
    // Function to make a request to the GPT API
    const requestToGpt = useCallback(async (prompt) => {

        // Create an entry for the user's message
        const userEntry = { sender: "user", message: prompt };
        // Update the chat history with the user's message
        setChatHistory([...chatHistory, userEntry]);

        // Set loading state to true and clear any previous errors
        setLoading(true);
        setError(null);

        try {
            // Make a POST request to the GPT API
            const { data } = await axios.post(production_url, { prompt }, {
                withCredentials: true,
                headders: {
                    "Content-Type": "application/json",
                }
            });
            // Create an entry for the AI's response
            const aiEntry = { sender: "ai", message: data };
            // Update the chat history with the AI's response
            setChatHistory(prevHistory => [...prevHistory, aiEntry]);
            // Set the GPT response
            setGptResponse(data);
        } catch (error) {
            // Set the error message
            setError(error.response ? error.response.data : error.message);
        } finally {
            // Set loading state to false
            setLoading(false);
        }
    }, [chatHistory]); // Include chatHistory and user as dependencies

    // Return the state variables and the request function
    return { gptResponse, loading, error, chatHistory, requestToGpt };
};

export default useGptRequest;
