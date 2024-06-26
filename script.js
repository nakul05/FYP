document.addEventListener('DOMContentLoaded', () => {
    const snapButton = document.getElementById('snapButton');
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const generateButton = document.getElementById('generateButton');

    if (snapButton) {

        
        let stream;

        // Get access to the camera
        async function startVideo() {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.play();
        }

        snapButton.addEventListener('click', startVideo);

        document.addEventListener('keydown', function(event) {
            if (event.key === 'q') {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                video.pause();
                stream.getTracks().forEach(track => track.stop());

                const imageDataUrl = canvas.toDataURL('image/png');

                fetch('/generate-response', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ image: imageDataUrl })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.feedback) {
                        localStorage.setItem('feedback', data.feedback);
                        window.location.href = '/feedback';
                    } else {
                        console.error('Error generating feedback:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });

       /*  snapButton.addEventListener('click', async () => {
            video.classList.remove('hidden');
            snapButton.classList.add('hidden');

            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.play();

            setTimeout(() => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const context = canvas.getContext('2d');
                context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
                video.pause();
                video.srcObject.getTracks().forEach(track => track.stop());

                const imageDataUrl = canvas.toDataURL('image/png');
                fetch('/get_results', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ image: imageDataUrl })
                })
                .then(response => response.json())
                .then(data => { console.log(data)
                    window.location.href = 'generate.html';
                })
                .catch(error => {
                    console.error(error); 
                });
            }, 3000);
        }); */
    }

    if (generateButton) {
        generateButton.addEventListener('click', () => {
            fetch('/generate-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                window.localStorage.setItem('feedback', data.feedback);
                window.location.href = 'feedback.html';
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    if (window.location.pathname.endsWith('feedback.html')) {
        const feedbackDiv = document.getElementById('feedback');
        const feedback = window.localStorage.getItem('feedback');
        feedbackDiv.textContent = feedback;
    }
});
