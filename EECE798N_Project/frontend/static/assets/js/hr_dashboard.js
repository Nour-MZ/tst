import { Chart } from "@/components/ui/chart"
document.addEventListener("DOMContentLoaded", () => {
  // Initialize department distribution chart
  const departmentChart = document.getElementById("departmentChart")

  if (departmentChart) {
    const ctx = departmentChart.getContext("2d")
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"],
        datasets: [
          {
            data: [35, 15, 25, 8, 12, 5],
            backgroundColor: [
              "#4299e1", // blue
              "#48bb78", // green
              "#ed8936", // orange
              "#9f7aea", // purple
              "#f56565", // red
              "#ecc94b", // yellow
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "right",
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.label || ""
                const value = context.raw || 0
                const total = context.dataset.data.reduce((a, b) => a + b, 0)
                const percentage = Math.round((value / total) * 100)
                return `${label}: ${value} (${percentage}%)`
              },
            },
          },
        },
      },
    })
  }

  // Task checkbox functionality
  const taskCheckboxes = document.querySelectorAll(".task-check")

  taskCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const taskItem = this.closest(".task-item")
      const taskTitle = taskItem.querySelector(".task-title")

      if (this.checked) {
        taskTitle.style.textDecoration = "line-through"
        taskTitle.style.color = "#a0aec0"
      } else {
        taskTitle.style.textDecoration = "none"
        taskTitle.style.color = ""
      }
    })
  })

  // Add task functionality
  const addTaskInput = document.querySelector(".add-task .form-input")
  const addTaskButton = document.querySelector(".add-task .btn")

  if (addTaskButton) {
    addTaskButton.addEventListener("click", () => {
      const taskText = addTaskInput.value.trim()

      if (taskText) {
        // Create new task item
        const taskList = document.querySelector(".task-list")
        const newTaskId = `task${taskList.children.length + 1}`

        const taskItem = document.createElement("li")
        taskItem.className = "task-item"
        taskItem.innerHTML = `
          <div class="task-checkbox">
            <input type="checkbox" id="${newTaskId}" class="task-check">
            <label for="${newTaskId}"></label>
          </div>
          <div class="task-content">
            <div class="task-title">${taskText}</div>
            <div class="task-meta">
              <span class="task-priority medium">Medium</span>
              <span class="task-due">Due in 3 days</span>
            </div>
          </div>
        `

        taskList.appendChild(taskItem)

        // Add event listener to new checkbox
        const newCheckbox = taskItem.querySelector(".task-check")
        newCheckbox.addEventListener("change", function () {
          const taskTitle = this.closest(".task-item").querySelector(".task-title")

          if (this.checked) {
            taskTitle.style.textDecoration = "line-through"
            taskTitle.style.color = "#a0aec0"
          } else {
            taskTitle.style.textDecoration = "none"
            taskTitle.style.color = ""
          }
        })

        // Clear input
        addTaskInput.value = ""
      }
    })

    // Allow adding task with Enter key
    addTaskInput.addEventListener("keyup", (e) => {
      if (e.key === "Enter") {
        addTaskButton.click()
      }
    })
  }
})
