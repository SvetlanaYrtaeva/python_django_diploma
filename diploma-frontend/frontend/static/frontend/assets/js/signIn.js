var mix = {
    methods: {
        signIn() {
            const username = document.querySelector(
                "#login",
            ).value.trim();

            const password = document.querySelector(
                "#password",
            ).value;

            if (
                !username
                || !password
            ) {
                alert(
                    "Введите логин и пароль.",
                );

                return;
            }

            this.postData(
                "/api/sign-in",
                {
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
                    : "Ошибка авторизации.";

                alert(message);
            });
        },
    },

    mounted() {},

    data() {
        return {};
    },
};