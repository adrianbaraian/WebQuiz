document.addEventListener("DOMContentLoaded", () => {
    fetchRandomSentences();

    document.getElementById("main-container").addEventListener("click", (event) => {
        if (event.target && event.target.id === "submit-button") {
            const questionsContainer = document.getElementById("main-container");
            const answers = [];

            questionsContainer.querySelectorAll(".question").forEach((questionElement) => {
                const questionId = questionElement.dataset.questionId;
                const answerField = questionElement.querySelector(".question-answer-field");

                if (answerField) {
                    answers.push({
                        id: questionId,
                        answer: answerField.value.trim(),
                    });
                }
            });

            console.log("Collected Answers:", answers);

            fetch("/api/submit-answers", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(answers),
            })
                .then((response) => response.json())
                .then((result) => {
                    console.log("Submission Result:", result);
                    displayFeedback(result.feedback);
                })
                .catch((error) => {
                    console.error("Error submitting answers:", error);
                    alert("An error occurred while submitting your answers.");
                });
        }
    });
});

function fetchRandomSentences() {
    fetch('/api/random-sentences')
        .then(response => response.json())
        .then(data => {
            const questionsContainer = document.getElementById("main-container");
            questionsContainer.innerHTML = "";

            data.forEach((question, index) => {
                const questionElement = document.createElement("div");
                questionElement.className = "question";
                questionElement.dataset.questionId = question.id;  // Add the question ID here
                questionElement.innerHTML =
                    `
                        <h3 class="question-title">Question ${index + 1}</h3>
                        <p><strong>English Sentence: </strong>${question.english_sentence}</p>
                        <p><strong>Difficulty: </strong>${question.difficulty}</p>
                        <p><strong>Use the following constants if any: </strong>${question.constants}</p>
                        <p><strong>Use the following predicates if any: </strong>${question.predicates}</p>
                        <form>
                            <label>Write the equivalent FOL sentence: </label><br>
                            <input type="text" id="question-${index + 1}" class="question-answer-field"><br>
                        </form>
                    `;
                questionsContainer.appendChild(questionElement);
            });
            const submitButton = document.createElement("input");
            submitButton.type = "submit";
            submitButton.value = "Submit Answers";
            submitButton.id = "submit-button";
            questionsContainer.appendChild(submitButton);
        })
        .catch(error => {
            console.error("Error fetching random sentences:", error);
        });
}

function displayFeedback(feedback) {
    const feedbackContainer = document.createElement("div");
    feedbackContainer.id = "feedback-container";

    feedback.forEach((item, index) => {
        const feedbackElement = document.createElement("div");
        feedbackElement.className = "feedback-item";
        feedbackElement.innerHTML = `
            <h3>Question ${index + 1}</h3>
            <p><strong>Your Answer:</strong> ${item.student_answer}</p>
            <p><strong>Model Answer:</strong> ${item.model_answer}</p>
            <p><strong>Result:</strong> ${item.result}</p>
            ${item.proof ? `<p><strong>Proof:</strong> ${item.proof}</p>` : ''}
        `;
        feedbackContainer.appendChild(feedbackElement);
    });

    const mainContainer = document.getElementById("main-container");
    mainContainer.innerHTML = "";
    mainContainer.appendChild(feedbackContainer);
}