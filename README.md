# GoTags

GoTags is a Sublime Text 3 plugin to append or remove tags for Golang struct.

Functionality includes:

- Append JSON tag with snake cased field name or remove JSON tag
- Append XML tag with snake cased field name or remove XML tag
- Append Xorm tag with xorm field type or remove Xorm tag

## Usage

Via the keyboard shortcut: `Super + G`, `Super + T` on OSX or `Ctrl + G`, `Ctrl + T` on other platforms. Then choice the action you want.

** Makesure line `type STRUCT_NAME struct{` in select region. **

For example:

```golang
type Example struct {
    Field1 int       ``         // int field
    Field2 string    `orig tag` // string field
    Field3 time.Time // time field
}
```

Then select `type Example struct {` line (or this is current line) and type the shortcut, select action `JSON: Append tags`:

```golang
type Example struct {
    Field1  int `json:"field1"`         // int field
    Field2  string  `orig tag json:"field2"` // string field
    Field3  time.Time   `json:"field3"` // time field
}
```

After save with gofmt:

```golang
type Example struct {
    Field1 int       `json:"field1"`          // int field
    Field2 string    `orig tag json:"field2"` // string field
    Field3 time.Time `json:"field3"`          // time field
}
```

## Idea from:

[gotag](https://github.com/suifengRock/gotag): golang auto generate struct tag.
