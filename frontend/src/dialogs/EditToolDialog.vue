<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="edit-tool-dialog-title" aria-modal="true" v-dialog="() => { newTool=false;toolErr='' }" @click.self="newTool=false;toolErr=''">
      <div class="modal" style="width:min(620px,95vw)"><div class="hd"><b id="edit-tool-dialog-title">{{(tForm.id?'Chỉnh sửa ':'Thêm ')+(tForm.mode==='cli'?'công cụ CLI':'endpoint')}}</b><button class="btn sm" @click="newTool=false;toolErr=''" aria-label="Đóng">✕</button></div>
        <div style="padding:16px 18px">
          <template v-if="tForm.mode!=='cli'">
            <p class="explain">Endpoint = URL đích máy chủ + một hoặc nhiều liên kết thông tin xác thực (cách Treg tự chèn từng khóa). Cần thêm khóa? Đóng hộp thoại này và mở mục <b>⚿ Khóa bí mật</b> trước.</p>
            <div class="frow"><label>Tên công cụ</label><input v-model="tForm.name" placeholder="ví dụ: openai"/></div>
            <p v-if="tForm.id && tForm.name.trim() && tForm.name.trim()!==tForm.oldName" class="sub" style="font-size:11px;margin-top:-4px">Đổi tên sẽ thay đổi cách Agent gọi: các kịch bản đang dùng <span class="mono">{{tForm.oldName}}</span> sẽ cần chuyển sang tên mới.</p>
            <div class="frow"><label>URL cơ sở</label><input v-model="tForm.base_url" placeholder="https://api.openai.com"/></div>
            <div class="lbl" style="margin-top:12px;display:flex;align-items:center">Liên kết xác thực — cách từng khóa được chèn <button class="btn sm" @click="addBinding" style="margin-left:auto">＋ Thêm liên kết</button></div>
            <div class="bindrow" v-for="(b,i) in tForm.bindings" :key="i">
              <select v-model="b.secret_id" class="msel">
                <option v-if="!secrets.length" :value="null" disabled>- thêm khóa bí mật -</option>
                <option v-for="s in secrets" :key="s.id" :value="s.id">{{s.name}}</option>
              </select>
              <select v-model="b.injector" class="msel"><option>env</option><option>oauth</option></select>
              <select v-model="b.location" class="msel"><option value="header">header</option><option value="query">query</option></select>
              <input v-model="b.name" placeholder="trường (Authorization)" class="bindinput"/>
              <input v-model="b.format" placeholder="Bearer {secret}" class="bindinput"/>
              <input v-if="b.injector==='oauth'" v-model="b.secret_field" placeholder="token" class="bindinput" style="max-width:80px;min-width:70px"/>
              <button v-if="tForm.bindings.length>1" class="btn sm" @click="removeBinding(i)" aria-label="Xóa liên kết">✕</button>
            </div>
            <p class="sub" style="font-size:11px"><span class="mono">{secret}</span> là giá trị khóa — ví dụ header <span class="mono">Authorization: Bearer {secret}</span>, hoặc query <span class="mono">api_key={secret}</span>. Mọi liên kết đều được áp dụng cho mỗi cuộc gọi.</p>
            <div class="frow" style="margin-top:10px">
              <label>Bộ nhớ đệm (TTL Cache)</label>
              <div style="display:flex;align-items:center;gap:8px;flex:1">
                <input type="number" min="0" max="86400" v-model.number="tForm.cache_ttl_seconds" placeholder="0" style="width:100px;padding:6px 8px"/>
                <span class="sub" style="font-size:11.5px">giây (0 = tắt cache; ví dụ 300 = lưu đệm 5 phút, tối đa 1MB/lượt)</span>
              </div>
            </div>
            <div class="frow" style="margin-top:8px">
              <label>Dự phòng khi lỗi (Smart Fallback)</label>
              <select v-model="tForm.fallback_tool_id" class="msel" style="flex:1">
                <option :value="null">— Không dùng dự phòng —</option>
                <option v-for="ot in (tools || []).filter(x => x.id !== tForm.id)" :key="ot.id" :value="ot.id">
                  {{ot.name}} ({{ot.base_url}})
                </option>
              </select>
            </div>
            <p class="sub" style="font-size:11px;margin-top:-4px">Khi API chính gặp lỗi 429 (Rate Limit) hoặc 5xx/Timeout, hệ thống sẽ tự động gọi sang công cụ dự phòng để Agent không bị gián đoạn.</p>
            <div class="frow" v-if="projects.length"><label>Dự án</label>
              <select v-model="tForm.project" class="msel">
                <option :value="null">— Toàn đội ngũ (mọi thành viên) —</option>
                <option v-for="p in projects" :key="p.id" :value="p.slug">{{p.name}}</option>
              </select></div>
            <p v-if="projects.length" class="sub" style="font-size:11px;margin-top:-4px">Tùy chọn. Mặc định là toàn đội ngũ. Dự án giúp giới hạn quyền chỉ cho những thành viên được phân quyền.</p>
          </template>
          <template v-else>
            <p class="explain">Thành viên chạy lệnh <span class="mono">treg run {{tForm.cli.bin||'&lt;cli&gt;'}} -- &lt;args&gt;</span> — Treg sẽ tự chèn khóa vào môi trường phiên chạy đó; khóa không bao giờ lưu trên máy người dùng.</p>
            <div class="frow"><label>Lệnh CLI</label><input v-model="tForm.cli.bin" :disabled="!!tForm.id" placeholder="ví dụ: gh" style="font-family:var(--mono)"/></div>
            <div class="frow"><label>Gói cài đặt</label><input v-model="tForm.cli.package" placeholder="cách cài đặt, ví dụ: brew install gh (tùy chọn)"/></div>
            <div class="frow"><label>API Base URL</label><input v-model="tForm.base_url" placeholder="https://api.github.com — máy chủ nhà cung cấp đằng sau CLI"/></div>
            <div class="lbl" style="margin-top:14px;display:flex;align-items:center">Biến môi trường khóa bí mật — chèn cho mỗi lượt chạy <button class="btn sm" @click="tForm.cli.inject.push({via:'env',name:'',secret_id:null})" style="margin-left:auto">＋ Thêm biến env</button></div>
            <div class="bindrow" v-for="(inj,i) in tForm.cli.inject" :key="'inj'+i">
              <select v-model="inj.secret_id" class="msel">
                <option v-if="!secrets.length" :value="null" disabled>- thêm khóa bí mật -</option>
                <option v-for="s in secrets" :key="s.id" :value="s.id">{{s.name}}</option>
              </select>
              <input v-model="inj.name" placeholder="tên biến env, ví dụ: GH_TOKEN" class="bindinput" style="font-family:var(--mono)"/>
              <button v-if="tForm.cli.inject.length>1" class="btn sm" @click="tForm.cli.inject.splice(i,1)" aria-label="Xóa biến env">✕</button>
            </div>
            <div class="frow" v-if="projects.length"><label>Dự án</label>
              <select v-model="tForm.project" class="msel">
                <option :value="null">— Toàn đội ngũ (mọi thành viên) —</option>
                <option v-for="p in projects" :key="p.id" :value="p.slug">{{p.name}}</option>
              </select>
            </div>
            <label class="cliopt"><span class="tswitch"><input type="checkbox" v-model="tForm.cli.enabled"/><span class="knob"></span></span><span style="flex:1;min-width:0"><b>Lượt chạy cục bộ (Local runs)</b><span class="sub" style="display:block;margin-top:2px">{{tForm.cli.enabled?'Bật — thành viên có thể chạy treg run '+(tForm.cli.bin||'công cụ')+' kèm khóa chèn tự động':'Tắt — từ chối mọi lượt chạy'}}</span></span></label>
            <div class="lbl" style="margin-top:14px;display:flex;align-items:center">Danh sách chặn (Deny list) — lệnh khớp quy tắc sẽ bị chặn trước khi chèn khóa <button class="btn sm" @click="tForm.cli.deny.push('')" style="margin-left:auto">＋ Thêm mẫu Regex</button></div>
            <p class="sub" style="font-size:11px;margin:4px 0 8px">Mỗi dòng là một Regex khớp với toàn bộ câu lệnh và từng đối số — dùng để chặn các lệnh thực thi code tùy ý (<span class="mono">(^|\s)run(\s|$)</span>) hoặc cờ chuyển hướng khóa (<span class="mono">--publish-url\b</span>).</p>
            <div class="bindrow" v-for="(p,i) in tForm.cli.deny" :key="'dn'+i">
              <input v-model="tForm.cli.deny[i]" placeholder="regex, ví dụ: (^|\s)run(\s|$)" class="bindinput" style="font-family:var(--mono)"/>
              <button class="btn sm" @click="tForm.cli.deny.splice(i,1)" aria-label="Xóa mẫu">✕</button>
            </div>
            <p class="sub" v-if="!tForm.cli.deny.length && !(tForm.cli.deny_defaults && catalogExtra.length)" style="font-size:11px;margin:4px 0 8px;color:var(--warn,#e0a458)">Chưa có rào chắn bảo vệ — bất kỳ lệnh {{tForm.cli.bin||'CLI'}} nào cũng sẽ nhận được khóa.</p>
            <label class="cliopt" v-if="catalogExtra.length"><span class="tswitch"><input type="checkbox" v-model="tForm.cli.deny_defaults"/><span class="knob"></span></span><span style="flex:1;min-width:0"><b>Mặc định từ Catalog</b><span class="sub" style="display:block;margin-top:2px">Các quy tắc chặn có sẵn từ danh mục cho {{tForm.cli.bin}} — được quản lý tập trung</span></span></label>
            <template v-if="tForm.cli.deny_defaults && catalogExtra.length">
              <div class="bindrow" v-for="(cp,ci) in catalogExtra" :key="'cd'+ci">
                <input :value="cp" disabled class="bindinput" style="font-family:var(--mono);opacity:.55"/>
                <span class="chip" title="Từ danh mục Treg — áp dụng cho mọi tổ chức">danh mục</span>
              </div>
            </template>
          </template>
          <div v-if="toolErr" class="banner">{{toolErr}}</div>
          <button class="btn primary" style="margin-top:6px" @click="saveTool" :disabled="toolBusy">{{toolBusy ? 'Đang lưu…' : (tForm.id ? 'Lưu thay đổi' : (tForm.mode==='cli' ? 'Tạo công cụ CLI' : 'Tạo endpoint'))}}</button>
        </div></div>
    </div>
</template>
