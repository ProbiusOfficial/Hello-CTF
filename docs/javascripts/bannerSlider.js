
    // 显示的图片下标
    let index = 0

    // 图片的数量
    let imageCount = document.querySelectorAll(
        ".carousel .container img"
    ).length

    let lastImageCount = 0; // 全局变量，用于跟踪上一次的图片数量
    let currentImageCount = imageCount

    const bottom = document.querySelector(".carousel .bottom")

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
            index++
            refresh()
        }, 3000)
    }

    // 自动滚动
    let autoTimer = createAuto()

    function refresh() {
        let currentImageCount = document.querySelectorAll(
            ".carousel .container img"
        ).length

        imageCount = currentImageCount

        function createIndicators() {
            const bottom = document.querySelector(".carousel .bottom");
            bottom.innerHTML = ''; // 清空现有的指示器

            for (let i = 0; i < imageCount; i++) {
                const indicator = document.createElement("div");
                indicator.classList.add("indicator");
                indicator.onclick = () => setIndex(i);
                bottom.append(indicator);
            }
        }

        // 检查图片数量是否发生变化
        if (currentImageCount !== lastImageCount) {
            createIndicators(); // 如果图片数量发生变化，则重新创建指示器
            lastImageCount = currentImageCount; // 更新记录的图片数量
        }


        if (index < 0) {
            // 下标小于 0 时
            // 设置最右的图片
            index = imageCount - 1
        } else if (index >= imageCount) {
            // 下标超过上限时
            // 设置最左的图片
            index = 0
        }

        // 获取轮播框元素
        let carousel = document.querySelector(".carousel")

        //获取轮播框的宽度
        let width = getComputedStyle(carousel).width
        width = Number(width.slice(0, -2))

        carousel.querySelector(".container").style.left =
            index * width * -1 + "px"
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

    let leftShift = refreshWrapper(() => {
        index--
    })
    let rightShift = refreshWrapper(() => {
        index++
    })

    let setIndex = refreshWrapper((idx) => {
        index = idx
    })
