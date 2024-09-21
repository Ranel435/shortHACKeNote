document.getElementById('addNote').addEventListener('click', function() {
  const noteInput = document.getElementById('noteInput');
  const noteText = noteInput.value.trim();

  if (noteText === '') {
    alert('Введите текст заметки!'); // Предупреждение, если заметка пустая
    return;
  }

  const notesList = document.getElementById('notesList');
  const listItem = document.createElement('li');
  listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
  listItem.textContent = noteText;

  const deleteButton = document.createElement('button');
  deleteButton.className = 'btn btn-danger btn-sm';
  deleteButton.textContent = 'Удалить';
  deleteButton.addEventListener('click', function() {
    notesList.removeChild(listItem); // Удаляем заметку
  });

  listItem.appendChild(deleteButton);
  notesList.appendChild(listItem); // Добавляем заметку в список
  noteInput.value = ''; // Очищаем поле ввода
});

function autoResizeTextarea(textarea) {
  textarea.style.height = 'auto'; // Сначала сбросить высоту
  textarea.style.height = textarea.scrollHeight + 'px'; // Установить высоту равной высоте содержимого
}

// Добавить обработчик события на textarea для обновления высоты при вводе текста
noteContent.addEventListener('input', function() {
  autoResizeTextarea(noteContent);
});

// Изначально установить высоту для уже существующих заметок
notes.forEach(note => {
  autoResizeTextarea(noteContent); // Применить к каждой заметке
});
