function displayFeedback(feedback, score) {
    const feedbackContainer = document.createElement("div");
    feedbackContainer.id = "feedback-container";

    if (!feedback || !Array.isArray(feedback)) {
        feedbackContainer.innerHTML = "<p>No feedback available.</p>";
        const mainContainer = document.getElementById("main-container");
        mainContainer.innerHTML = "";
        mainContainer.appendChild(feedbackContainer);
        return;
    }

    feedback.forEach((item, index) => {
        const feedbackElement = document.createElement("div");
        feedbackElement.className = "feedback";
        feedbackElement.innerHTML = `
            <h3>Question ${index + 1}</h3>
            <p><strong>Your Answer:</strong> ${item.student_answer}</p>
            <p><strong>Model Answer:</strong> ${item.model_answer}</p>
            <p><strong>Result:</strong> ${item.result}</p>
            ${item.proof ? `<p><strong>Proof:</strong> ${item.proof}</p>` : ''}
        `;
        feedbackContainer.appendChild(feedbackElement);
    });

    const scoreElement = document.createElement("div");
    scoreElement.className = "score";
    scoreElement.innerHTML = `<h3>Total Score: ${score}/10</h3>`;
    feedbackContainer.appendChild(scoreElement);

    const mainContainer = document.getElementById("main-container");
    mainContainer.innerHTML = "";
    mainContainer.appendChild(feedbackContainer);
}

document.addEventListener("DOMContentLoaded", () => {
    fetchRandomSentences();

    document.getElementById("main-container").addEventListener("click", (event) => {
        if (event.target && event.target.id === "submit-button") {
            const questionsContainer = document.getElementById("main-container");
            const answers = [];

            let allFieldsFilled = true;

            questionsContainer.querySelectorAll(".question").forEach((questionElement) => {
                const questionId = questionElement.dataset.questionId;
                const answerField = questionElement.querySelector(".question-answer-field");

                if (answerField) {
                    const answer = answerField.value.trim();
                    if (answer === "") {
                        allFieldsFilled = false;
                    } else {
                        answers.push({
                            id: questionId,
                            answer: answer,
                        });
                    }
                }
            });

            if (!allFieldsFilled) {
                alert("Please fill in all answer fields.");
                return;
            }

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
                    displayFeedback(result.feedback, result.score);
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

            const sentences = Array.isArray(data) ? data : [data];

            sentences.forEach((question, index) => {
                const questionElement = document.createElement("div");
                questionElement.className = "question";
                questionElement.dataset.questionId = question.id;
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