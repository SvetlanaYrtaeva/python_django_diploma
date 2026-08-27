var mix = {
    methods: {
        signUp() {
            const name = document.querySelector(
                "#name",
            ).value.trim();

            const username = document.querySelector(
                "#login",
            ).value.trim();

            const password = document.querySelector(
                "#password",
            ).value;

            if (
                !name
                || !username
                || !password
            ) {
                alert(
                    "Заполните все поля.",
                );

                return;
            }

            this.postData(
                "/api/sign-up",
                {
                    name,
                    username,
                    password,
                },
            ).then(() => {
                location.assign("/");
            }).catch((error) => {
                const message = (
                    error.response
                    && error.response.data
                    && error.response.data.detail
                )
                    ? error.response.data.detail
                    : "Ошибка регистрации.";

                alert(message);
            });
        },
    },

    mounted() {},

    data() {
        return {};
    },
};