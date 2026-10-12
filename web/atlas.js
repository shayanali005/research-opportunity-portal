'use strict';
const $ = (selector) => document.querySelector(selector);
const form = $('#opportunityForm');
const state = {rows: [], selected: null, deleting: null, loading: false};
const fields = ['research_title','research_description','research_area','faculty_name','department','required_skills','available_positions','application_deadline','status'];
function node(tag, text, className) { const el = document.createElement(tag); if(text !== undefined) el.textContent = text; if(className) el.className = className; return el; }
function notice(message, error = false) { $('#notice').textContent = message; $('#notice').className = 'notice' + (error ? ' error' : ''); $('#notice').hidden = false; }
async function api(path = '', options = {}) {
  const response = await fetch('/api/opportunities' + path, {...options, headers:{'Content-Type':'application/json', ...options.headers}});
  let data; try { data = await response.json(); } catch { throw new Error('The server returned an unreadable response.'); }
  if(!response.ok) throw new Error([data.error || 'Request failed.', ...(data.details || [])].join(' '));
  return data;
}
function badge(status) { return node('span', status === 'Open' ? '● Open' : '● Closed', 'badge' + (status === 'Closed' ? ' closed' : '')); }
function date(value) { return new Intl.DateTimeFormat('en-GB', {day:'numeric',month:'short',year:'numeric'}).format(new Date(value + 'T12:00:00')); }
function render() {
  const search = $('#search').value.trim().toLowerCase(), status = $('#statusFilter').value;
  const rows = state.rows.filter(row => (!status || row.status === status) && ['research_title','research_area','faculty_name','department'].some(key => row[key].toLowerCase().includes(search)));
  const sort = $('#sort').value;
  rows.sort((a,b) => sort === 'newest' ? b.id-a.id : sort === 'title' ? a.research_title.localeCompare(b.research_title) : a.application_deadline.localeCompare(b.application_deadline) || b.id-a.id);
  $('#total').textContent = state.rows.length;
  const open = state.rows.filter(row => row.status === 'Open');
  $('#openCount').textContent = open.length;
  $('#positions').textContent = open.reduce((sum,row) => sum + row.available_positions, 0);
  $('#boardTitle').textContent = status === 'Open' ? 'Open calls' : status === 'Closed' ? 'Closed archive' : 'All opportunities';
  document.querySelectorAll('[data-filter]').forEach(button => {button.classList.toggle('active', button.dataset.filter === status); button.setAttribute('aria-pressed', String(button.dataset.filter === status));});
  $('#resultCount').textContent = rows.length + (rows.length === 1 ? ' opportunity' : ' opportunities') + ' in this view';
  const container = $('#cards'); container.replaceChildren();
  if(!rows.length) {const empty = node('div', undefined, 'empty'); empty.append(node('h3', state.rows.length ? 'No matching opportunities' : 'Your next discovery starts here'), node('p', state.rows.length ? 'Try another search or status filter.' : 'Publish a research call to add the first opportunity.')); container.append(empty);}
  for(const row of rows) {
    const card = node('article', undefined, 'opportunity'), top = node('div', undefined, 'card-top');
    top.append(node('span', row.research_area, 'area'), badge(row.status));
    card.append(top, node('h3', row.research_title), node('p', row.research_description, 'description'), node('div', row.faculty_name, 'faculty'), node('div', row.department, 'department'));
    const bottom = node('div', undefined, 'card-bottom'), meta = node('div', row.available_positions + ' position' + (row.available_positions === 1 ? '' : 's'), 'meta');
    meta.append(node('strong', 'Apply by ' + date(row.application_deadline)));
    const view = node('button', 'View details ↗', 'view-button'); view.setAttribute('aria-label', 'View details: ' + row.research_title); view.onclick = () => showDetails(row.id);
    bottom.append(meta, view); card.append(bottom); container.append(card);
  }
}
async function refresh() {
  if(state.loading) return;
  state.loading = true; $('#refresh').disabled = true;
  try {state.rows = (await api()).data; render();}
  catch(error) {notice(error.message, true); $('#resultCount').textContent = 'Unable to refresh. Check the server and try again.';}
  finally {state.loading = false; $('#refresh').disabled = false;}
}
function openEditor(row = null) {
  form.reset(); form.elements.id.value = row ? row.id : '';
  fields.forEach(key => { form.elements[key].setCustomValidity(''); if(row) form.elements[key].value = row[key]; });
  $('#editorTitle').textContent = row ? 'Edit research call' : 'Publish a new call';
  $('#save').textContent = row ? 'Save changes' : 'Publish opportunity'; $('#formError').hidden = true;
  if($('#details').open) $('#details').close(); $('#editor').showModal();
}
async function showDetails(identifier) {
  try {
    const row = (await api('/' + identifier)).data; state.selected = row;
    const content = $('#detailContent'); content.replaceChildren(badge(row.status), node('h2', row.research_title, 'detail-title'), node('p', row.research_description, 'detail-description'));
    const grid = node('dl', undefined, 'detail-grid');
    for(const [label,value] of [['Reference','RA-' + row.id],['Research area',row.research_area],['Faculty member',row.faculty_name],['Department',row.department],['Required skills',row.required_skills],['Positions',row.available_positions],['Application deadline',date(row.application_deadline)]]) {const group = node('div'); group.append(node('dt',label),node('dd',value)); grid.append(group);}
    content.append(grid);
    const actions = $('#detailActions'); actions.replaceChildren();
    const del = node('button','Delete','quiet'); del.onclick = () => {state.deleting = row.id; $('#deleteError').hidden = true; $('#confirmation').showModal();};
    const toggle = node('button',row.status === 'Open' ? 'Close call' : 'Reopen call','quiet');
    toggle.onclick = async () => {toggle.disabled = true; try {await api('/'+row.id,{method:'PUT',body:JSON.stringify({status:row.status === 'Open' ? 'Closed' : 'Open'})}); await showDetails(row.id); notice('Opportunity status updated.'); await refresh();} catch(error) {notice(error.message,true); $('#details').close();} finally {toggle.disabled = false;}};
    const edit = node('button','Edit opportunity','primary'); edit.onclick = () => openEditor(row);
    actions.append(del,toggle,edit); if(!$('#details').open) $('#details').showModal();
  } catch(error) {notice(error.message,true);}
}
form.addEventListener('input', event => event.target.setCustomValidity?.(''));
form.addEventListener('submit', async event => {
  event.preventDefault(); const body = {};
  for(const key of fields) { const input = form.elements[key]; const value = input.value.trim(); if(!value) {input.setCustomValidity('Please complete this field.'); input.reportValidity(); return;} body[key] = key === 'available_positions' ? Number(value) : value; }
  if(new TextEncoder().encode(body.research_description).length > 65535) {$('#formError').textContent = 'The description is too long (maximum 65,535 UTF-8 bytes).'; $('#formError').hidden = false; return;}
  $('#save').disabled = true; $('#formError').hidden = true;
  const identifier = form.elements.id.value;
  try { const result = await api(identifier ? '/' + identifier : '', {method:identifier ? 'PUT' : 'POST',body:JSON.stringify(body)}); $('#editor').close(); notice(result.message); await refresh(); }
  catch(error) {$('#formError').textContent = error.message; $('#formError').hidden = false;}
  finally {$('#save').disabled = false;}
});
$('#confirmDelete').onclick = async () => {
  $('#confirmDelete').disabled = true;
  try {await api('/' + state.deleting,{method:'DELETE'}); $('#confirmation').close(); $('#details').close(); notice('Opportunity deleted.'); await refresh();}
  catch(error) {$('#deleteError').textContent = error.message; $('#deleteError').hidden = false;}
  finally {$('#confirmDelete').disabled = false;}
};
document.querySelectorAll('[data-close]').forEach(button => button.onclick = () => $('#' + button.dataset.close).close());
document.querySelectorAll('[data-filter]').forEach(button => button.onclick = () => {$('#statusFilter').value = button.dataset.filter; render();});
$('#create').onclick = $('#sideCreate').onclick = () => openEditor();
$('#refresh').onclick = () => {$('#notice').hidden = true; refresh();};
$('#search').oninput = $('#statusFilter').onchange = $('#sort').onchange = render;
refresh();
