function getArray(response) {
    if (Array.isArray(response)) {
        return response;
    }

    if (
        response
        && Array.isArray(response.items)
    ) {
        return response.items;
    }

    if (
        response
        && Array.isArray(response.results)
    ) {
        return response.results;
    }

    if (
        response
        && Array.isArray(response.products)
    ) {
        return response.products;
    }

    return [];
}


function normalizeProduct(product) {
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
}


function catalogParams(app) {
    return {
        "filter[name]": app.filters.name || "",

        "filter[minPrice]": (
            app.filters.price.currentFromValue
            ?? app.filters.minPrice
            ?? 0
        ),

        "filter[maxPrice]": (
            app.filters.price.currentToValue
            ?? app.filters.maxPrice
            ?? 500000
        ),

        "filter[freeDelivery]": Boolean(
            app.filters.freeDelivery,
        ),

        "filter[available]": Boolean(
            app.filters.available,
        ),

        currentPage: Number(
            app.currentPage || 1,
        ),

        sort: app.selectedSort
            || "price",

        sortType: app.sortType
            || "inc",

        limit: Number(
            app.limit || 20,
        ),
    };
}


const catalogMixin = {
    data() {
        return {
            catalogFromServer: [],
            currentPage: 1,
            total: 0,
            limit: 20,
            selectedSort: "price",
            sortType: "inc",
        };
    },

    methods: {
        getCatalog() {
            this.getData(
                "/api/catalog",
                catalogParams(this),
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
                    (product) => normalizeProduct(
                        product,
                    ),
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

    mounted() {
        this.getCatalog();
    },
};


window.catalogMixin = catalogMixin;