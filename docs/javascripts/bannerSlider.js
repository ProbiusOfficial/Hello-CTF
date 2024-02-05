document$.subscribe(function () {
    // 显示的图片下标
    let index = 0

    // 图片的数量
    let imageCount = document.querySelectorAll(".carousel img").length

    if (imageCount <= 0)
        // 当前页面不需要轮播图……
        return

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
        indicator.onclick = () => {
            index = i
            refresh()
        }

        bottom.append(indicator)
    }

    let timeoutID = setTimeout(() => {
        index = (index + 1) % imageCount
        refresh()
    }, 3000)

    function refresh() {
        clearTimeout(timeoutID)
        // 获取轮播框的宽度
        try {
            let width = carousel.clientWidth
            carouselContainer.style.left = index * width * -1 + "px"
        } catch (err) {
            console.log(err)
        }

        timeoutID = setTimeout(() => {
            index = (index + 1) % imageCount
            refresh()
        }, 3000)
    }

    document.querySelector(".carousel-btn.left").onclick = () => {
        index = (index - 1 + imageCount) % imageCount
        refresh()
    }

    document.querySelector(".carousel-btn.right").onclick = () => {
        index = (index + 1) % imageCount
        refresh()
    }
})
