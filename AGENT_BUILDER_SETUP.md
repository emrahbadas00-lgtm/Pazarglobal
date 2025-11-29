# Agent Builder UI Setup Checklist

## 🎯 Overview
Bu doküman OpenAI Agent Builder'da yapılması gereken tüm UI konfigürasyonlarını adım adım açıklar.

---

## 📡 Step 1: MCP Server Connection

### Railway MCP Server URL
```
https://pazarglobal-production.up.railway.app/sse
```

### Tools to Connect (6 total)
- [x] `clean_price_tool` - Fiyat temizleme
- [x] `insert_listing_tool` - Yeni ilan oluşturma (✨ user_id eklendi)
- [x] `search_listings_tool` - İlan arama
- [x] `update_listing_tool` - İlan güncelleme (✨ user_id eklendi)
- [x] `delete_listing_tool` - İlan silme
- [x] `list_user_listings_tool` - Kullanıcı ilanlarını listeleme

### How to Connect
1. Agent Builder → Settings → Tools
2. "Add MCP Server" → Enter URL
3. Test connection → Should show 6 tools
4. Enable all tools

---

## 🤖 Step 2: RouterAgent Configuration

### Current State
- ❌ Eski RouterAgent instructions kullanıyor
- ❌ Delete intent misclassification (vazgeç vs sil conflict)
- ❌ Priority logic eksik

### Action Required
1. **Replace ENTIRE RouterAgent instructions** with:
   ```
   File: agent_instructions/RouterAgent_Updated.md
   ```

2. **Critical Changes in New Version:**
   - ✅ `delete_listing` intent HIGHEST priority
   - ✅ If "ilan" + "sil" → ALWAYS delete_listing (even if "vazgeç" present)
   - ✅ 4 new test examples from production logs
   - ✅ Fixed: "ilanı silebilir miyiz" → delete_listing (NOT cancel)
   - ✅ Fixed: "scooter ilanını silemiyormuyuz" → delete_listing (NOT cancel)

3. **Verify Output Format:**
   ```json
   {"intent": "delete_listing"}
   ```

### Testing Commands
After update, test with:
- ✅ "ilanı silebilir miyiz" → Expected: `{"intent": "delete_listing"}`
- ✅ "vazgeçtim" (WITHOUT "ilan") → Expected: `{"intent": "cancel"}`
- ✅ "fiyatını değiştir" → Expected: `{"intent": "update_listing"}`

---

## 🔧 Step 3: UpdateListingAgent Configuration

### Current State
- ❌ Tools not connected
- ❌ Agent says: "sistem tarafında ilan güncelleme aracına erişimim yok"

### Action Required
1. **Add Tools to UpdateListingAgent:**
   - ✅ `list_user_listings_tool` - List user's listings first
   - ✅ `update_listing_tool` - Update selected listing
   - ✅ `clean_price_tool` - Clean price if user provides "22 bin TL"

2. **Instructions File:**
   ```
   File: agent_instructions/UpdateListingAgent.md
   ```

3. **Key Rules to Verify:**
   - ⚠️ **ASLA insert_listing_tool KULLANMA** (critical rule)
   - Workflow: list → select → clean_price (if needed) → update → confirm
   - Handle 4 scenarios: price, content, status, multiple fields

### Tool Usage Flow
```
User: "fiyatını 3000 yap"
  ↓
Agent: list_user_listings_tool(user_id="...")
  ↓
Agent: "Hangi ilanınızı güncellemek istersiniz?" (show list)
  ↓
User: "2. sıradaki"
  ↓
Agent: update_listing_tool(listing_id="...", price=3000)
  ↓
Agent: "✅ Fiyat 3000 TL olarak güncellendi"
```

---

## 🗑️ Step 4: DeleteListingAgent Configuration

### Current State
- ❌ NOT wired in if/else block
- ❌ Router outputs `{"intent": "delete_listing"}` but no route to agent

### Action Required
1. **Add Tools to DeleteListingAgent:**
   - ✅ `list_user_listings_tool` - List user's listings
   - ✅ `delete_listing_tool` - Delete after confirmation

2. **Wire If/Else Block:**
   ```javascript
   if (input.output_parsed.intent == "delete_listing") {
     goto DeleteListingAgent
   }
   ```

3. **Instructions File:**
   ```
   File: agent_instructions/DeleteListingAgent.md
   ```

4. **Key Rules to Verify:**
   - ⚠️ **MUTLAKA onay al** - "Evet"/"Hayır"
   - ⚠️ **Onay almadan ASLA silme**
   - Scenario 5: "vazgeçtim" during delete → Cancel gracefully
   - Safety: "⚠️ TÜM İLANLARINIZI silmek istediğinizden emin misiniz?"

### Tool Usage Flow
```
User: "ilanı sil"
  ↓
Agent: list_user_listings_tool(user_id="...")
  ↓
Agent: "Hangi ilanınızı silmek istersiniz?" (show list)
  ↓
User: "iPhone ilan"
  ↓
Agent: "🗑️ '{title}' ilanını silmek istediğinizden emin misiniz? (Evet/Hayır)"
  ↓
User: "Evet"
  ↓
Agent: delete_listing_tool(listing_id="...")
  ↓
Agent: "✅ İlan başarıyla silindi"
```

---

## ✅ Step 5: Verify All Agents Have Tools

### CreateListingAgent
- [x] `clean_price_tool`
- [x] `insert_listing_tool`

### SearchProductAgent
- [x] `search_listings_tool`

### UpdateListingAgent (⚠️ NEEDS UPDATE)
- [ ] `list_user_listings_tool` ← ADD
- [ ] `update_listing_tool` ← ADD
- [ ] `clean_price_tool` ← ADD

### DeleteListingAgent (⚠️ NEEDS CREATION)
- [ ] `list_user_listings_tool` ← ADD
- [ ] `delete_listing_tool` ← ADD

### PublishListingAgent
- [ ] `list_user_listings_tool` (if needed)
- [ ] `update_listing_tool` (to change status to 'active')

### SmallTalkAgent
- [x] No tools needed

### CancelAgent
- [x] No tools needed

---

## 🔀 Step 6: If/Else Block Routing

### Current If/Else Structure
```javascript
if (input.output_parsed.intent == "create_listing") {
  goto CreateListingAgent
}
else if (input.output_parsed.intent == "search_product") {
  goto SearchProductAgent
}
else if (input.output_parsed.intent == "update_listing") {
  goto UpdateListingAgent  // ⚠️ Tools not connected yet
}
else if (input.output_parsed.intent == "delete_listing") {
  // ❌ MISSING - ADD THIS
  goto DeleteListingAgent
}
else if (input.output_parsed.intent == "publish_listing") {
  goto PublishListingAgent
}
else if (input.output_parsed.intent == "cancel") {
  goto CancelAgent
}
else {
  goto SmallTalkAgent
}
```

### Action Required
1. **Add delete_listing route** (between update_listing and publish_listing)
2. Verify all routes have corresponding agents
3. Test each route with Router output

---

## 🧪 Step 7: End-to-End Testing

### Test Cases

#### Test 1: Delete Intent Classification
```
Input: "ilanı silebilir miyiz"
Expected Router Output: {"intent": "delete_listing"}
Expected Route: DeleteListingAgent
Expected Tools Called: list_user_listings_tool → delete_listing_tool
```

#### Test 2: Update Intent with Tool
```
Input: "fiyatını 5000 tl yap"
Expected Router Output: {"intent": "update_listing"}
Expected Route: UpdateListingAgent
Expected Tools Called: list_user_listings_tool → update_listing_tool
Expected NO Error: "erişimim yok"
```

#### Test 3: Cancel vs Delete Distinction
```
Input: "vazgeçtim" (no "ilan" keyword)
Expected Router Output: {"intent": "cancel"}
Expected Route: CancelAgent

Input: "ilanımı silmekten vazgeçtim" (has "ilan" + "sil")
Expected Router Output: {"intent": "delete_listing"}
Expected Route: DeleteListingAgent
Then: Agent should handle cancellation gracefully (Scenario 5)
```

#### Test 4: List User Listings
```
Input: "ilanlarımı göster"
Expected Router Output: {"intent": "update_listing"} OR direct call
Expected Tools Called: list_user_listings_tool(user_id="test-user-uuid")
Expected Output: List of user's listings with titles, prices, status
```

#### Test 5: Multiple Updates
```
Input: "fiyatı 3000 yap ve açıklamasını 'yeni açıklama' olarak değiştir"
Expected Router Output: {"intent": "update_listing"}
Expected Tools Called: 
  - list_user_listings_tool
  - update_listing_tool(price=3000, description="yeni açıklama")
```

---

## 📋 Pre-Launch Checklist

### MCP Server
- [x] 6 tools registered
- [x] user_id parameter added to insert_listing
- [x] user_id parameter added to update_listing
- [x] Deployed to Railway
- [x] SSE endpoint accessible

### RouterAgent
- [ ] Replace with RouterAgent_Updated.md
- [ ] Verify priority logic (delete > cancel)
- [ ] Test 4 new examples
- [ ] Verify JSON output format

### UpdateListingAgent
- [ ] Add 3 tools (list_user_listings, update_listing, clean_price)
- [ ] Upload UpdateListingAgent.md instructions
- [ ] Test: "fiyatını değiştir" should work
- [ ] Verify: NO "erişimim yok" error

### DeleteListingAgent
- [ ] Create new agent
- [ ] Add 2 tools (list_user_listings, delete_listing)
- [ ] Upload DeleteListingAgent.md instructions
- [ ] Wire if/else: delete_listing → DeleteListingAgent
- [ ] Test: "ilanı sil" → shows listings → requires confirmation

### If/Else Block
- [ ] Add delete_listing condition
- [ ] Verify all 7 routes work
- [ ] Test each intent classification

### End-to-End
- [ ] Test all 5 test cases above
- [ ] Verify no "tool unavailable" errors
- [ ] Check Router classification accuracy
- [ ] Confirm confirmation flow for delete

---

## 🚨 Common Issues & Solutions

### Issue 1: "sistem tarafında ilan güncelleme aracına erişimim yok"
**Cause:** Tools not added to UpdateListingAgent  
**Solution:** Add `update_listing_tool`, `list_user_listings_tool`, `clean_price_tool` in Agent Builder UI

---

### Issue 2: Router still classifying "ilanı sil" as "cancel"
**Cause:** Old RouterAgent instructions still active  
**Solution:** REPLACE (not append) with RouterAgent_Updated.md completely

---

### Issue 3: DeleteListingAgent not triggered
**Cause:** If/else block missing delete_listing condition  
**Solution:** Add condition: `input.output_parsed.intent == "delete_listing"` → DeleteListingAgent

---

### Issue 4: user_id parameter error
**Cause:** Old tool version without user_id  
**Solution:** Railway auto-deployed new version with default UUID. Agent Builder should auto-detect new parameter.

---

### Issue 5: MCP tools not appearing
**Cause:** Server connection failed or tools not enabled  
**Solution:** 
1. Test SSE endpoint: https://pazarglobal-production.up.railway.app/sse
2. Re-add MCP server in Agent Builder
3. Enable all 6 tools

---

## 🎯 Success Criteria

✅ All checks must pass:

1. Router correctly classifies all 7 intents
2. UpdateListingAgent can call update_listing_tool without error
3. DeleteListingAgent wired and requires confirmation
4. "ilanı silebilir miyiz" → delete_listing (NOT cancel)
5. "fiyatını değiştir" → no "erişimim yok" error
6. All 6 MCP tools connected and callable
7. user_id parameter visible in tool schemas

---

## 📝 Next Steps After UI Setup

Once all above steps complete:

1. **Phase 2: WhatsApp Integration**
   - Replace test UUID with real phone-based user_id
   - Conversation context tracking
   - Message history

2. **Phase 3: Dashboard Development**
   - Admin panel for listings
   - Analytics dashboard
   - User management

3. **Production Hardening**
   - Enable RLS with auth.uid()
   - Rate limiting
   - Error monitoring
   - Backup strategy

---

## 📞 Support

If issues persist:
1. Check Railway logs: https://railway.app/project/pazarglobal/deployments
2. Test tools locally: `python server.py`
3. Verify Supabase connection: `python check_supabase.py`
4. Review agent instructions: `agent_instructions/` folder
