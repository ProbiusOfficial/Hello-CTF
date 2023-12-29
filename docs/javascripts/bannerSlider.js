document$.subscribe(function () {
    // 显示的图片下标
    let index = 0

    // 图片的数量
    let imageCount = document.querySelectorAll(".carousel img").length

    // incidators container
    const bottom = document.querySelector(".carousel-bottom")

    // 轮播框元素
    let carousel = document.querySelector(".carousel")
    let carouselContainer = document.querySelector(".carousel-container")

    for (let i = 0; i < imageCount; i++) {
        // DOM 操作
        // 创建底部按钮
        const indicator = document.createElement("div")
        indicator.classList.add("indicator")
        indicator.onclick = () => setIndex(i)

        bottom.append(indicator)
    }

    function createAuto() {
        return setInterval(() => {
            index = (index + 1) % imageCount
            refresh()
        }, 3000)
    }

    // 自动滚动
    let autoTimer = createAuto()

    function refresh() {
        //获取轮播框的宽度
        let width = carousel.clientWidth

        carouselContainer.style.left = index * width * -1 + "px"
    }

    let refreshWrapper = (func) => {
        // refresh 装饰器
        return function (...args) {
            let result = func(...args)
            refresh()

            // 重置自动滚动
            clearInterval(autoTimer)
            autoTimer = createAuto()
            return result
        }
    }

    let setIndex = refreshWrapper((idx) => {
        index = idx
    })

    document.querySelector(".carousel-btn.left").onclick = refreshWrapper(
        () => {
            index = (index - 1 + imageCount) % imageCount
        }
    )

    document.querySelector(".carousel-btn.right").onclick = refreshWrapper(
        () => {
            index = (index + 1) % imageCount
        }
    )
})
