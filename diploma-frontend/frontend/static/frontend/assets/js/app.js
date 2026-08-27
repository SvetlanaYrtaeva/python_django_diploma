const { createApp } = Vue;


function getCookie(name) {
    let cookieValue = null;

    if (
        document.cookie
        && document.cookie !== ""
    ) {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (
                cookie.substring(
                    0,
                    name.length + 1,
                ) === `${name}=`
            ) {
                cookieValue = decodeURIComponent(
                    cookie.substring(
                        name.length + 1,
                    ),
                );

                break;
            }
        }
    }

    return cookieValue;
}


function getArray(response) {
    if (Array.isArray(response)) {
        return response;
    }

    if (
        response
        && Array.isArray(response.results)
    ) {
        return response.results;
    }

    if (
        response
        && Array.isArray(response.items)
    ) {
        return response.items;
    }

    if (
        response
        && Array.isArray(response.products)
    ) {
        return response.products;
    }

    return [];
}


function normalizeBasket(response) {
    const items = getArray(response);
    const basket = {};

    items.forEach((item) => {
        const productId = Number(
            item.product_id
            ?? item.id,
        );

        const count = Number(
            item.count
            ?? item.quantity
            ?? 0,
        );

        const price = Number(
            item.price
            ?? 0,
        );

        if (!productId) {
            return;
        }

        basket[productId] = {
            ...item,
            id: productId,
            product_id: productId,
            count,
            quantity: count,
            price,
        };
    });

    return basket;
}


function getErrorMessage(
    error,
    defaultMessage,
) {
    if (
        error
        && error.response
        && error.response.data
        && error.response.data.detail
    ) {
        return error.response.data.detail;
    }

    return defaultMessage;
}


createApp({
    delimiters: [
        "${",
        "}$",
    ],

    data() {
        return {
            filters: {
                price: {
                    minValue: 1,
                    maxValue: 500000,
                    currentFromValue: 0,
                    currentToValue: 50000,
                },

                name: "",
                minPrice: 0,
                maxPrice: 50000,
                freeDelivery: false,
                available: true,
            },

            sortRules: [
                {
                    id: "rating",
                    title: "Популярности",
                },
                {
                    id: "price",
                    title: "Цене",
                },
                {
                    id: "reviews",
                    title: "Отзывам",
                },
                {
                    id: "date",
                    title: "Новизне",
                },
            ],

            topTags: [],
            categories: [],
            catalogFromServer: [],
            orders: [],
            cart: [],
            paymentData: {},
            basket: {},
            searchText: "",

            total: 0,
            limit: 20,
            currentPage: 1,
            selectedSort: "price",
            sortType: "inc",
        };
    },

    methods: {
        getCookie(name) {
            return getCookie(name);
        },

        postData(
            url,
            payload = {},
            headers = {},
        ) {
            const csrfToken = this.getCookie(
                "csrftoken",
            );

            return axios.post(
                url,
                payload,
                {
                    withCredentials: true,

                    headers: {
                        "X-CSRFToken": csrfToken,
                        "Content-Type": (
                            "application/json"
                        ),
                        ...(headers || {}),
                    },
                },
            ).then((response) => {
                return {
                    data: response.data,
                    status: response.status,
                };
            }).catch((error) => {
                const status = (
                    error.response
                    && error.response.status
                )
                    ? error.response.status
                    : "network error";

                const message = getErrorMessage(
                    error,
                    "Ошибка запроса",
                );

                console.warn(
                    `Метод '${url}' вернул статус ${status}: ${message}`,
                );

                throw error;
            });
        },

        getData(
            url,
            params = {},
        ) {
            return axios.get(
                url,
                {
                    params,
                    withCredentials: true,
                },
            ).then((response) => {
                return response.data;
            }).catch((error) => {
                const status = (
                    error.response
                    && error.response.status
                )
                    ? error.response.status
                    : "network error";

                console.warn(
                    `Метод '${url}' вернул статус ${status}`,
                );

                throw error;
            });
        },

        search() {
            const value = encodeURIComponent(
                this.searchText || "",
            );

            location.assign(
                `/catalog/?filter=${value}`,
            );
        },

        getCategories() {
            this.getData(
                "/api/categories",
            ).then((response) => {
                this.categories = getArray(
                    response,
                );
            }).catch(() => {
                console.warn(
                    "Ошибка получения категорий",
                );

                this.categories = [];
            });
        },

        getBasket() {
            this.getData(
                "/api/basket",
            ).then((response) => {
                this.basket = normalizeBasket(
                    response,
                );
            }).catch(() => {
                console.warn(
                    "Ошибка получения корзины",
                );

                this.basket = {};
            });
        },

        setBasket(
            response,
        ) {
            this.basket = normalizeBasket(
                response,
            );
        },

        addToBasket(
            item,
            count = 1,
        ) {
            const productId = Number(
                item.product_id
                ?? item.id,
            );

            const quantity = Number(
                count,
            );

            if (
                !productId
                || quantity <= 0
            ) {
                console.warn(
                    "Не удалось определить товар",
                );

                return;
            }

            this.postData(
                "/api/basket",
                {
                    id: productId,
                    count: quantity,
                },
            ).then(({ data }) => {
                this.setBasket(
                    data,
                );

                alert(
                    "Товар добавлен в корзину.",
                );
            }).catch((error) => {
                const message = getErrorMessage(
                    error,
                    "Ошибка добавления товара в корзину.",
                );

                console.warn(message);
                alert(message);
            });
        },

        removeFromBasket(
            id,
            count = 1,
        ) {
            const productId = Number(id);
            const quantity = Number(count);

            if (
                !productId
                || quantity <= 0
            ) {
                return;
            }

            axios.delete(
                "/api/basket",
                {
                    data: {
                        id: productId,
                        count: quantity,
                    },

                    withCredentials: true,

                    headers: {
                        "X-CSRFToken": this.getCookie(
                            "csrftoken",
                        ),
                        "Content-Type": (
                            "application/json"
                        ),
                    },
                },
            ).then((response) => {
                this.setBasket(
                    response.data,
                );
            }).catch((error) => {
                const message = getErrorMessage(
                    error,
                    "Ошибка удаления товара из корзины.",
                );

                console.warn(message);
                alert(message);
            });
        },

        submitBasket() {
            location.assign(
                "/orders/checkout/customer/",
            );
        },

        signOut() {
            this.postData(
                "/api/sign-out",
                {},
            ).then(() => {
                location.assign("/");
            }).catch((error) => {
                console.warn(
                    getErrorMessage(
                        error,
                        "Ошибка выхода из аккаунта.",
                    ),
                );

                location.assign("/");
            });
        },

        getCatalog() {
            const params = {
                "filter[name]": this.filters.name || "",

                "filter[minPrice]": (
                    this.filters.price.currentFromValue
                    ?? this.filters.minPrice
                    ?? 0
                ),

                "filter[maxPrice]": (
                    this.filters.price.currentToValue
                    ?? this.filters.maxPrice
                    ?? 500000
                ),

                "filter[freeDelivery]": Boolean(
                    this.filters.freeDelivery,
                ),

                "filter[available]": Boolean(
                    this.filters.available,
                ),

                currentPage: Number(
                    this.currentPage || 1,
                ),

                sort: this.selectedSort
                    || "price",

                sortType: this.sortType
                    || "inc",

                limit: Number(
                    this.limit || 20,
                ),
            };

            this.getData(
                "/api/catalog",
                params,
            ).then((response) => {
                const products = getArray(
                    response,
                );

                console.log(
                    "Ответ API:",
                    response,
                );

                console.log(
                    "Массив после getArray:",
                    products,
                );

                this.catalogFromServer = products.map(
                    (product) => {
                        const image = product.image || {};

                        return {
                            ...product,

                            id: Number(
                                product.id,
                            ),

                            title: (
                                product.title
                                || product.name
                                || ""
                            ),

                            name: (
                                product.name
                                || product.title
                                || ""
                            ),

                            slug: product.slug || "",

                            imageSrc: (
                                image.src
                                || ""
                            ),

                            imageAlt: (
                                image.alt
                                || product.title
                                || product.name
                                || ""
                            ),

                            price: Number(
                                product.price
                                || 0,
                            ),

                            oldPrice: Number(
                                product.old_price
                                || 0,
                            ),

                            url: (
                                product.url
                                || `/product/${product.slug}/`
                            ),
                        };
                    },
                );

                console.log(
                    "Товары после нормализации:",
                    this.catalogFromServer,
                );

                this.total = Number(
                    response.total
                    ?? response.count
                    ?? this.catalogFromServer.length,
                );

                this.currentPage = Number(
                    response.currentPage
                    || 1,
                );

                this.limit = Number(
                    response.limit
                    || 20,
                );
            }).catch((error) => {
                console.warn(
                    "Ошибка получения каталога:",
                    error,
                );

                this.catalogFromServer = [];
                this.total = 0;
            });
        },
    },

    computed: {
        basketCount() {
            return Object.values(
                this.basket || {},
            ).reduce(
                (
                    result,
                    item,
                ) => {
                    const count = Number(
                        item.count
                        ?? item.quantity
                        ?? 0,
                    );

                    const price = Number(
                        item.price
                        ?? 0,
                    );

                    result.count += count;
                    result.price += count * price;

                    return result;
                },
                {
                    count: 0,
                    price: 0,
                },
            );
        },
    },

    mounted() {
        this.getCategories();
        this.getBasket();
        this.getCatalog();
    },
}).mount("#site");